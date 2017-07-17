import simpy
import math
import random
import pandas as pd
import numpy as np
from copy import deepcopy
import PhotoVoltaics
from MomentaryAcknowledged import MomentaryAcknowledged

class House(object):
    def __init__(self, index, global_data, file_name,grid=True, pv=False):
        self.id = index
        self.global_data = global_data
        self.file_name = file_name
        self.env = global_data.env
        self.type = 'house'
        self.monitor = global_data.monitor
        self.bus = global_data.message_bus
        self.random_factor = random.random()
        self.message_response_queue = simpy.Store(self.env)
        self.sent_tids = []
        self.confirmed_transactions = []

        self.plot = self.monitor.add_plot()-1
        # self.plot2 = self.monitor.add_plot()-1

        self.demand = 0
        self.forecast = {'value': 0, 'begin': 0, 'end': 0}
        self.momentary_acknowledged_supply = MomentaryAcknowledged(self.env)

        self.global_data.message_bus.add_message_subscriber(self.message_handler)

        if grid:
            self.grid = self.global_data.grid

        if pv:
            self.pv = PhotoVoltaics.PhotoVoltaics(global_data, self)

        self.action = self.env.process(self.strategy())
        self.action = self.env.process(self.live())
        self.action = self.env.process(self.monitor_high_frequency())

    def strategy(self):
        while True:
            request_pause = 60

            if self.request_condition():
                request_forecast = deepcopy(self.forecast)

                request_forecast['value'] = request_forecast['value'] - self.momentary_acknowledged_supply.sum(begin=request_forecast['begin'],
                                                                                                               end=request_forecast['end'])

                msg_data = {'sender': self.id, 'type': self.type, 'forecast': request_forecast}
                tid = random.getrandbits(128)
                msg = self.bus.Message('/pv/from/req', msg_data, self.env.now, tid)
                self.sent_tids.append(tid)
                self.env.process(self.bus.send(msg))
                yield self.env.timeout(self.bus.timeout*5)


                request_forecast = deepcopy(self.forecast)
                request_forecast['value'] = request_forecast['value'] - self.momentary_acknowledged_supply.sum(begin=request_forecast['begin'],
                                                                                                               end=request_forecast['end'])

                msg_data = {'sender': self.id, 'type': self.type, 'forecast': request_forecast}
                tid = random.getrandbits(128)
                msg = self.bus.Message('/grid/from/req', msg_data, self.env.now, tid)
                self.sent_tids.append(tid)
                self.env.process(self.bus.send(msg))


                yield self.env.timeout(self.bus.timeout)
            yield self.env.timeout(request_pause)

    def request_condition(self):
        # print("[{}]".format(self.env.now))
        # print("[{}] {} > {}".format(self.env.now, self.forecast['value'], self.momentary_acknowledged.sum(begin=self.forecast['begin'],
        #                                                                 end=self.forecast['end'])))
        return self.forecast['value'] > self.momentary_acknowledged_supply.sum(begin=self.forecast['begin'],
                                                                               end=self.forecast['end'])

    def live(self):
        _dat = pd.read_csv('data/{}'.format(self.file_name), header=None, delimiter=';')
        demand = _dat[_dat[_dat.columns[1]].values == 'Wirkenergie A+ 15']
        self.demands = np.nan_to_num(demand[demand.columns[4]].values) / 0.25 / 1000  # kW

        while True:
            requestPause = 60
            self.demand = self.demands[int(math.floor(self.env.now / 900))]

            self.forecast['value'] = self.demands[int(math.floor(self.env.now / 900)) + 1]
            self.forecast['begin'] = (int(math.floor(self.env.now / 900)) + 1) * 15 * 60
            self.forecast['end'] = (int(math.floor(self.env.now / 900)) + 2) * 15 * 60

            yield self.env.timeout(requestPause)

    def message_handler(self, msg):
        if (msg.topic == '/house/to/ack') and (msg.tid in self.sent_tids):
            self.sent_tids.remove(msg.tid)
            print("[{:.3f}] HOUSE[{}]: message in, topic: {}, acknowledged: {}".format(self.env.now, self.id, msg.topic, msg.data['acknowledged']))
            acknowledged = deepcopy(msg.data['acknowledged'])

            if acknowledged['value'] <= self.forecast['value'] - self.momentary_acknowledged_supply.sum(begin=self.forecast['begin'],
                                                                                                        end=self.forecast['end']):

                msg = self.bus.Message('/{}/from/ack'.format(msg.data['type']), {'acknowledged': acknowledged}, self.env.now, msg.tid)
                self.env.process(self.bus.send(msg))

                self.momentary_acknowledged_supply.append(acknowledged)
                self.confirmed_transactions.append(msg)

        yield self.env.exit()

    def monitor_high_frequency(self):
        self.monitor.plots[self.plot]['plot'].setTitle("HOUSE[{}]".format(self.id))

        while True:
            request_pause = 60
            self.monitor.append_data(self.plot, 0, self.env.now, self.demand)
            # self.monitor.append_data(self.plot, 1, self.env.now, self.forecast['value'])
            self.monitor.append_data(self.plot, 1, self.env.now, self.momentary_acknowledged_supply.sum())

            yield self.env.timeout(request_pause)
