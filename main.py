import simpy
import GlobalData
import MessageBus
import Blockchain
import House
import Monitor
from os import listdir
from PyQt5 import QtGui


if (__name__ == '__main__'):
    app = None
    sim_start = 21600 + 86400 * 100
    sim_stop = sim_start + 21600 + 86400 * 0

    if not app:
        app = QtGui.QApplication([])

    monitor = Monitor.Monitor(sim_start=sim_start)

    env = simpy.Environment(initial_time=sim_start)

    message_bus = MessageBus.MessageBus(env)
    global_data = GlobalData.GlobalData(env, monitor.graph, message_bus, debug=True)

    blockchain = Blockchain.Blockchain(global_data)

    data_files = listdir('data')

    houses = []
    houses.append(House.House(0, global_data, data_files[0], pv=True))
    houses.append(House.House(1, global_data, data_files[1], pv=True))
    houses.append(House.House(2, global_data, data_files[2], pv=True))
    #houses.append(House.House(3, global_data, data_files[3], pv=True))
    #houses.append(House.House(4, global_data, data_files[4], pv=True))
    #houses.append(House.House(5, global_data, data_files[5], pv=True))
    # houses.append(House.House(5, global_data, data_files[6], pv=True))
    # houses.append(House.House(5, global_data, data_files[7], pv=True))
    # houses.append(House.House(5, global_data, data_files[8], pv=True))
    # houses.append(House.House(5, global_data, data_files[9], pv=True))

    global_data.houses = houses
    monitor.show()

    env.run(until=sim_stop)
    monitor.graph.refresh()

    houses[0].print_confirmed_transactions()

    print(len(blockchain.ledger))
    for ind in range(len(blockchain.ledger)):
        msg = blockchain.ledger[ind]
        print('[{:.0f}] {}\t{} -> {} : \t{} | {}'.format(msg.receive_time, msg.topic, msg.data['sender'], msg.data['receiver'], msg.data['acknowledged'], msg.tid))

    print(len(houses[0].pv.confirmed_transactions))
    for ind in range(len(houses[0].pv.confirmed_transactions)):
        msg = houses[0].pv.confirmed_transactions[ind]
        print('[{}] {} {}'.format(ind, msg.topic, msg.data['type']))

    if (app):
        app.exec_()
