import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui


class Monitor(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Monitor, self).__init__(parent)

        self.setWindowTitle("Energy Balance")
        self.setGeometry(200,200,800,300)
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setSpacing(10)
        # self.layout.addWidget(settings_GUI(self.layout))
        self.graph = Graph(0)
        self.layout.addWidget(self.graph)


class Graph(QtGui.QGroupBox):
    def __init__(self, module, parent=None):
        super(Graph, self).__init__(parent)
        self.setTitle("Load module number {}".format(module))

        layout = QtGui.QVBoxLayout()

        self.plotItem = pg.GraphicsLayoutWidget()

        layout.addWidget(self.plotItem)
        self.plots=[]
        # self.plots.append({'xData':[],'yData':[],'plot':self.plotItem.addPlot()})

        # btn = QtGui.QPushButton("Cancel job.")
        # layout.addWidget(btn)

        self.setLayout(layout)

    def add_plot(self):
        self.plots.append({'xData':[],'yData':[],'plot':self.plotItem.addPlot()})
        # print("LENGTH:", len(self.plots))
        return len(self.plots)

    def append_data(self, plot, graph, x, y):
        if len(self.plots[plot]['xData']) < (graph+1):
            self.plots[plot]['xData'].append([])
        if len(self.plots[plot]['yData']) < (graph+1):
            self.plots[plot]['yData'].append([])

        self.plots[plot]['xData'][graph].append(x)
        self.plots[plot]['yData'][graph].append(y)

    def refresh_view(self, plot):
        self.plots[plot]['plot'].plot(self.plots[plot]['xData'], self.plots[plot]['yData'])

    def refresh(self):
        for plot in self.plots:
            i = 0
            for graph in range(len(plot['xData'])):
                i = i + 1
                yData = plot['yData'][graph]
                plot['plot'].plot(plot['xData'][graph], yData, pen=(i,len(plot['xData'])))
