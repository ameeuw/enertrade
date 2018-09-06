class MomentaryAcknowledged(object):
    def __init__(self, global_data, type, id):
        self.type = type
        self.id = id
        self.env = global_data.env
        self.global_data = global_data
        self.values = []
        self.action = self.env.process(self.watchdog())

    def append(self, acknowledged):
        if self.global_data.debug:
            print('[{:.3f}] {}[{}]:\tAPPENDED: {}'.format(self.env.now, str.upper(self.type), self.id, acknowledged))
        self.values.append(acknowledged)

    def remove(self, acknowledged):
        if acknowledged in self.values:
            self.values.remove(acknowledged)
            if self.global_data.debug:
                print('[{:.3f}] {}[{}]:\tREMOVED -f: {}'.format(self.env.now, str.upper(self.type), self.id, acknowledged))
        else:
            if self.global_data.debug:
                print('[{:.3f}] {}[{}]:\tFAILED TO REMOVE: {} '.format(self.env.now, str.upper(self.type), self.id, acknowledged))



    def watchdog(self):
        while True:
            request_pause = 15
            for element in self.values:
                if element['end'] < self.env.now:
                    self.values.remove(element)
                    if self.global_data.debug:
                        print('[{:.3f}] {}[{}]:\tREMOVED: {}'.format(self.env.now, str.upper(self.type), self.id, element))
            # print('[{}] Watchdog: {}'.format(self.env.now, self.values))
            yield self.env.timeout(request_pause)

    def sum_until(self, until):
        temp_sum = 0
        for element in self.values:
            if element['end'] >= until:
                temp_sum += element['value']
        return temp_sum

    def sum(self, begin=None, end=None):
        temp_sum = 0
        if begin is None:
            begin = self.env.now
        if end is None:
            end = self.env.now+1

        for element in self.values:
            if (element['begin'] <= begin) and (element['end'] >= end):
                temp_sum += element['value']

        return temp_sum