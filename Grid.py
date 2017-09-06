import math, random
from copy import deepcopy
from MomentaryAcknowledged import MomentaryAcknowledged


class Grid(object):
    def __init__(self, global_data):
        self.env = global_data.env
        self.global_data = global_data
        self.id = 0
        self.type = 'grid'
        self.bus = global_data.message_bus
        self.bus.add_message_subscriber(self.message_handler)
        self.monitor = global_data.monitor
        self.momentary_acknowledged_load = MomentaryAcknowledged(self.global_data)
        self.momentary_acknowledged_supply = MomentaryAcknowledged(self.global_data)
        self.pending_tids = []
        self.confirmed_transactions = []

        self.plot = self.monitor.add_plot()-1

        self.action = self.env.process(self.strategy())
        self.action = self.env.process(self.live())
        self.action = self.env.process(self.monitor_high_frequency())

    def strategy(self):
        while True:
            request_pause = 1 + random.random()
            # self.monitor.appendData(self.plot, 0, self.env.now, self.load)
            yield self.env.timeout(request_pause)

    def acknowledge_condition(self):
        return True

    def accept_condition(self):
        return True

    def live(self):
        while True:
            request_pause = (1 * 60) + random.random()
            yield self.env.timeout(request_pause)

    def message_handler(self, msg):
        if msg.topic == '/grid/to/req':
            if self.global_data.debug:
                print("[{:.3f}] GRID: message in, topic: {}, forecast: {}".format(self.env.now, msg.topic, msg.data['forecast']))

            request_tid = msg.tid
            request_forecast = msg.data['forecast']
            acknowledged = request_forecast
            acknowledged['value'] = acknowledged['value']
            self.momentary_acknowledged_supply.append(acknowledged)
            msg_data = {'sender': self.id, 'receiver': msg.data['sender'], 'type': self.type, 'acknowledged': acknowledged}
            msg = self.bus.Message('/{}/from/ack'.format(msg.data['type']), msg_data, self.env.now, request_tid)
            self.env.process(self.bus.send(msg))

        if (msg.topic == '/grid/to/ack'):
            pass

        if (msg.topic == '/grid/from/ack') and (msg.tid in self.pending_tids):
            self.pending_tids.remove(msg.tid)
            acknowledged = deepcopy(msg.data['acknowledged'])
            self.momentary_acknowledged_load.append(acknowledged)
            self.confirmed_transactions.append(msg)

        if msg.topic == '/grid/from/req':
            if self.global_data.debug:
                print("[{:.3f}] GRID: message in, topic: {}, forecast: {}".format(self.env.now, msg.topic, msg.data['forecast']))

            acknowledged = deepcopy(msg.data['forecast'])
            if acknowledged['value'] > 0:
                msg_data = {'sender': self.id, 'receiver': msg.data['sender'], 'type': self.type, 'acknowledged': acknowledged}
                msg = self.bus.Message('/{}/to/ack'.format(msg.data['type']), msg_data, self.env.now, msg.tid)
                self.pending_tids.append(msg.tid)
                self.env.process(self.bus.send(msg))

        yield self.env.exit()

    def monitor_high_frequency(self):
        self.monitor.plots[self.plot]['plot'].setTitle("GRID")
        while True:
            request_pause = 60
            self.monitor.append_data(self.plot, 0, self.env.now, self.momentary_acknowledged_load.sum())
            self.monitor.append_data(self.plot, 1, self.env.now, self.momentary_acknowledged_supply.sum())
            yield self.env.timeout(request_pause)
