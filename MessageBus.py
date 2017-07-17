import simpy
from _collections import deque
from numpy import mean

msgBuffer = 100


class MessageBus(object):
    """
    A Broadcast pipe that allows one process to send messages to many.

    This construct is useful when message consumers are running at
    different rates than message generators and provides an event
    buffering to the consuming processes.

    The parameters are used to create a new

    Args:
        :class:`~simpy.resources.store.Store` instance each time
        :meth:`get_output_conn()` is called.

    """
    class Message(object):
        def __init__(self, topic, data, timestamp, tid=None):
            self.topic = topic
            self.data = data
            self.timestamp = timestamp
            self.tid = tid
            self.queue_time = None
            self.transmit_time = None
            self.receive_time = None

    def __init__(self, env, capacity=1):
        self.env = env
        self.capacity = capacity
        self.max_queue_length = 0
        self.average_queue_length = 0
        self.pipes = []
        self.timeout = 0.1
        self.message_subscribers = []
        self.connection = self.connect()
        self.env.process(self.receive())

    def put(self, msg):
        '@type msg: CANmessage'
        """
        Broadcast a message to all receivers.

        Args:
            msg : CANmessage to send out
        """

        yield self.env.timeout(0.001)

        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        #events = [store.put(msg) for store in self.pipes]
        for store in self.pipes:
            store.put(msg)

        if len(self.pipes[0].put_queue) > self.max_queue_length:
            self.max_queue_length = len(self.pipes[0].put_queue)

        # self.averageQueueLength += len(self.pipes[0].put_queue)
        # self.averageQueueLengthSamples += 1.0

        if len(self.pipes[0].put_queue) > msgBuffer:
            raise RuntimeError('Buffer overflow!!! '+ str(len(self.pipes[0].put_queue)) + " messages in queue!")
        # return self.env.all_of(events)  # Condition event for all "events"

    def connect(self):
        """
        Get a new output connection for this broadcast pipe.

        Returns:
            pipe (Store) : :class:`~simpy.resources.store.Store`.

        """
        pipe = simpy.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe

    def receive(self):
        '@type msg: CANmessage'

        #print("Starting message receiver")
        while True:
            msg = yield self.connection.get()

            # yield self.env.timeout(0.001)
            msg.receive_time = self.env.now
            # print('at time %f: [topic] %s  [data] %s' %(self.env.now, msg.topic, msg.data))

            for sub in self.message_subscribers:
                # print("Calling "+ sub.__name__)
                self.env.process(sub(msg))


    def send(self, msg):
        '@type msg: CANmessage'
        # msg.queueTime = self.env.now
        yield self.env.process(self.put(msg))
        # print("Incoming data: ", msg)
        #print("CANSend"+str(msg.data))
        #self.env.process(self.put(msg))
        #yield self.put(msg)

    def add_message_subscriber(self,subObject):
        #print("Added MessageSubscriber " + subObject.__name__)
        self.message_subscribers.append(subObject)

if (__name__ == '__main__'):
    pass
