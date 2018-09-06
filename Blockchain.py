

class Blockchain(object):
    def __init__(self, global_data):
        self.env = global_data.env
        self.global_data = global_data
        self.id = 0
        self.type = 'chain'
        self.bus = global_data.message_bus
        self.bus.add_message_subscriber(self.message_handler)
        self.monitor = global_data.monitor

        #self.plot = self.monitor.add_plot()-1

        self.action = self.env.process(self.monitor_high_frequency())

        self.ledger = []

    def message_handler(self, msg):
        if msg.topic == '/blockchain/sendRawTx':
            self.ledger.append(msg)

            if self.global_data.debug:
                print("[{:.3f}] {}[{}]:\tmessage in, topic: {}, forecast: {} | {}".format(self.env.now,
                                                                                          str.upper(self.type), self.id,
                                                                                          msg.topic,
                                                                                          msg.data['acknowledged'],
                                                                                          msg.tid))

        yield self.env.exit()

    def monitor_high_frequency(self):
        # self.monitor.plots[self.plot]['plot'].setTitle("Blockchain")
        while True:
            request_pause = 60
            # self.monitor.append_data(self.plot, 0, self.env.now, self.momentary_acknowledged_load.sum())
            yield self.env.timeout(request_pause)
