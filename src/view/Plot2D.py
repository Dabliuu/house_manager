
from functools import partial

# for plotting:
#import matplotlib
import pyqtgraph as pg

import numpy as np
from collections import deque
#from PySide.QtGui import QVBoxLayout
from numpy import arange, sin, cos, pi

from Colors import GRIS_CLARO, NEGRO_LEVE, AZUL_CLARO, ROJO_OSCURO

class Plot2D(pg.GraphicsWindow):
    def __init__(self, widget, name=None, x_label="time", y_label="value"):

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', GRIS_CLARO)
        pg.setConfigOption('foreground', NEGRO_LEVE) # the text and labels color

        # for the inheritance specifications:
        super(Plot2D, self).__init__(parent=widget)

        # constants
        self.sample_time = 20
        self.sample_frequency = 1/20
        self.num_points = 100
        
        # the data points data structures
        self.time_queue = deque(np.linspace(0, self.num_points * self.sample_time, self.num_points))
        self.value_queue = deque(np.zeros(len(self.time_queue)))

        # to add this widget to the widget parent:
        layout = pg.QtGui.QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(self)

        # the traces managment:
        self.traces = dict()
        self.name = name

        if name!=None:
            self.plot1 = self.addPlot() #(title = None)
        else:
            self.plot1 = self.addPlot()
        
        self.plot1.setLabels(left = y_label)
        self.plot1.setLabels(bottom = x_label)


    def trace(self, name, dataset_x, dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x, dataset_y)
            self.plot1.autoRange()
        else:
            self.traces[name] = self.plot1.plot(pen = {'color': ROJO_OSCURO, 'width': 4} )
        
        

    def shift_value(self, new_value, graph=None):
        if graph == None:
            graph = self.name

        new_time = self.time_queue[-1] + self.sample_time
        self.time_queue.append(new_time)
        self.time_queue.popleft()

        self.value_queue.append(new_value)
        self.value_queue.popleft()
        self.trace(graph, self.time_queue, self.value_queue)

    def resize_plot(self, new_size):
        length = len(self.time_queue)
        self.num_points = new_size
        if new_size > length:
            n = new_size - length
            self.value_queue = deque(
                np.concatenate(
                        (np.zeros(n), np.array(self.value_queue)), 
                        axis=0
                )
            )
            last_value = np.array(self.time_queue)[-1]
            self.time_queue = deque(np.linspace(last_value - new_size * self.sample_time, last_value, new_size))
        elif new_size < length:
            n = length - new_size
            for i in range(n):
                self.time_queue.popleft()
                self.value_queue.popleft()
            

    def start(self, handler=None):
        
        if handler==None:
            handler = self.default_partial_handler 

        # timer execution
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(handler)
        self.timer.start(self.sample_time * 1000) #this is in ms

        if self.name in self.traces:
            self.plot1.setMouseEnabled(x=False, y=False) # this is disabling the mouse scroll zoom

    def stop(self):
        self.timer.stop()
        
        if self.name in self.traces:
            self.plot1.setMouseEnabled(x=True, y=True)
    
    def set_new_timer(self, sample_time):
        self.sample_time = sample_time
        
        if self.timer.isActive():
            self.timer.start(sample_time * 1000)
    
    def default_partial_handler(self):
                
        new_time = self.time_queue[-1] + self.sample_time
        self.time_queue.append(new_time)
        self.time_queue.popleft()

        new_value = sin(2 * pi * new_time / 5)
        self.value_queue.append(new_value)
        self.value_queue.popleft()

        self.trace("sin", self.time_queue, self.value_queue)
        #self.trace("cos", self.time, self.c)