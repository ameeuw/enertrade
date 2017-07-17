import random
import Grid


class GlobalData(object):
    def __init__(self, env, monitor, message_bus):
        self.env = env
        self.monitor = monitor
        self.message_bus = message_bus
        self.grid = Grid.Grid(self)

    def getTid(self):
        return random.getrandbits(128)


    def simprint(self, string):
        print("[{}] {}".format(self.env.now, string))
