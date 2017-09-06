class MomentaryAcknowledged(object):
    def __init__(self, global_data):
        self.env = global_data.env
        self.global_data = global_data
        self.values = []
        self.action = self.env.process(self.watchdog())

    def append(self, acknowledged):
        if self.global_data.debug:
            print('[{:.3f}] APPENDED: {}'.format(self.env.now, acknowledged))
        self.values.append(acknowledged)

    def watchdog(self):
        while True:
            request_pause = 15
            for element in self.values:
                if element['end'] < self.env.now:
                    self.values.remove(element)
                    if self.global_data.debug:
                        print('[{:.3f}] REMOVED: {}'.format(self.env.now, element))
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