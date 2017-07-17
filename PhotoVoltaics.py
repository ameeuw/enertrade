import math, random
import pandas as pd
import numpy as np
from MomentaryAcknowledged import MomentaryAcknowledged
import copy

class PhotoVoltaics(object):
    def __init__(self, global_data, house):
        self.env = global_data.env
        self.house = house
        self.id = house.id
        self.type = 'pv'
        self.monitor = global_data.monitor
        self.plot = self.monitor.add_plot()-1
        self.bus = global_data.message_bus
        self.bus.add_message_subscriber(self.message_handler)
        self.sent_tids = []
        self.confirmed_transactions = []

        self.supply = 0
        self.forecast = {'value': 0, 'begin': 0, 'end': 0}

        self.momentary_acknowledged_load = MomentaryAcknowledged(self.env)

        self.action = self.env.process(self.strategy())
        self.action = self.env.process(self.live())
        self.action = self.env.process(self.monitor_high_frequency())

    def strategy(self):
        while True:
            request_pause = 5 * 60 + 5 * random.random()
            # TODO: bring sending mechanics to pv system
            if self.send_condition():
                # print("[{:.3f}]\n\nSEND CONDITION\n\n".format(self.env.now))

                request_forecast = copy.deepcopy(self.forecast)
                request_forecast['value'] = request_forecast['value'] - self.momentary_acknowledged_load.sum(begin=request_forecast['begin'],
                                                                                                             end=request_forecast['end'])

                msg_data = {'sender': self.id, 'type': self.type, 'forecast': request_forecast}
                tid = random.getrandbits(128)
                msg = self.bus.Message('/grid/to/req', msg_data, self.env.now, tid)
                self.sent_tids.append(tid)
                self.env.process(self.bus.send(msg))

                pass

            yield self.env.timeout(request_pause)

    def acknowledge_condition(self):
        return True

    def send_condition(self):
        return self.forecast['value'] > self.momentary_acknowledged_load.sum(begin=self.forecast['begin'],
                                                                             end=self.forecast['end'])

    def live(self):
        _dat = pd.read_csv('data/{}'.format(self.house.file_name), header=None, delimiter=';')
        production = _dat[_dat[_dat.columns[1]].values == 'Wirkenergie A- 15']
        self.production = np.nan_to_num(production[production.columns[4]].values) / 0.25 / 1000  # kW

        while True:
            request_pause = 60

            self.supply = self.production[int(math.floor(self.env.now / 900))]

            self.forecast['value'] = self.production[int(math.floor(self.env.now / 900)) + 1]
            self.forecast['begin'] = (int(math.floor(self.env.now / 900)) + 1) * 15 * 60
            self.forecast['end'] = (int(math.floor(self.env.now / 900)) + 2) * 15 * 60

            yield self.env.timeout(request_pause)

    def message_handler(self, msg):
        if (msg.topic == '/pv/from/ack') and (msg.tid in self.sent_tids):
            self.sent_tids.remove(msg.tid)
            print("[{:.3f}] PV[{}]: message in, topic: {}, acknowledged: {}".format(self.env.now, self.id, msg.topic,
                                                                                    msg.data['acknowledged']))
            acknowledged = copy.deepcopy(msg.data['acknowledged'])
            self.momentary_acknowledged_load.append(acknowledged)

            self.confirmed_transactions.append(msg)


        if msg.topic == '/pv/from/req':
            print("[{:.3f}] PV[{}] message in, topic: {}, forecast: {}".format(self.env.now, self.id, msg.topic,
                                                                               msg.data['forecast']))

            request_tid = msg.tid
            request_forecast = msg.data['forecast']
            acknowledged = copy.deepcopy(request_forecast)
            acknowledgable = self.forecast['value'] - self.momentary_acknowledged_load.sum(begin=request_forecast['begin'],
                                                                                           end=request_forecast['end'])

            acknowledged['value'] = min(acknowledgable, acknowledged['value'])

            if acknowledged['value'] > 0:
                self.momentary_acknowledged_load.append(acknowledged)
                msg_data = {'sender': self.id, 'receiver': msg.data['sender'], 'type': self.type, 'acknowledged': acknowledged}
                msg = self.bus.Message('/{}/to/ack'.format(msg.data['type']), msg_data, self.env.now, request_tid)
                self.env.process(self.bus.send(msg))

            self.confirmed_transactions.append(msg)

        yield self.env.exit()

    def monitor_high_frequency(self):
        self.monitor.plots[self.plot]['plot'].setTitle("PV[{}]".format(self.id))
        while True:
            request_pause = 60
            self.monitor.append_data(self.plot, 0, self.env.now, self.supply)
            # self.monitor.append_data(self.plot, 1, self.env.now, self.forecast['value'])
            self.monitor.append_data(self.plot, 1, self.env.now, self.momentary_acknowledged_load.sum())
            yield self.env.timeout(request_pause)