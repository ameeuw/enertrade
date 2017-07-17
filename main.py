import simpy
import GlobalData
import MessageBus
import House
import Monitor
from os import listdir
from PyQt4 import QtGui


if (__name__ == '__main__'):
    app = None
    sim_start = 21600 + 86400 * 100
    sim_stop = sim_start + 43200 + 86400 * 0

    if not app:
        app = QtGui.QApplication([])

    monitor = Monitor.Monitor()

    env = simpy.Environment(initial_time=sim_start)

    message_bus = MessageBus.MessageBus(env)
    global_data = GlobalData.GlobalData(env, monitor.graph, message_bus)


    data_files = listdir('data')

    houses = []
    houses.append(House.House(0, global_data, data_files[0], pv=True))
    houses.append(House.House(1, global_data, data_files[1], pv=True))
    # houses.append(House.House(2, global_data, data_files[2], pv=True))
    # houses.append(House.House(3, global_data, data_files[3], pv=True))
    # houses.append(House.House(4, global_data, data_files[4], pv=True))
    # houses.append(House.House(5, global_data, data_files[5], pv=True))
    # houses.append(House.House(5, global_data, data_files[6], pv=True))
    # houses.append(House.House(5, global_data, data_files[7], pv=True))
    # houses.append(House.House(5, global_data, data_files[8], pv=True))
    # houses.append(House.House(5, global_data, data_files[9], pv=True))

    global_data.houses = houses
    monitor.show()

    env.run(until=sim_stop)
    monitor.graph.refresh()


    if (app):
        app.exec_()