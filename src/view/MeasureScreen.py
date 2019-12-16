import time
import logging
import threading
from functools import partial
import json
from datetime import timedelta  
import csv
import datetime
import platform

from tkinter.filedialog import asksaveasfile
from tkinter import Tk

import os 
from os.path import expanduser
from threading import Thread

from BackgroundTimer import BackgroundTimer
from Plot2D import Plot2D

import numpy as np
from numpy import pi, sin, cos, tan

from collections import OrderedDict 


from random import random
import concurrent.futures


class MeasureScreen():

    def __init__(self, View):

        self.View = View


        # configure the sensor selector (combo box)
        self.View.window.measure_selector.currentIndexChanged.connect(self.on_measure_selector)


        # the 2 list that will hold the objects for the graphs
        self.graph_names = list()
        self.active_graphs = list()
        
        # create the graph names vector from the serial number and the active graphs helper
        for index, data_type in enumerate(self.View.currentConfig["data_types"]):

            serial_number = self.View.currentConfig["serial_numbers"][index]
            print("--->>> MeasurScreen, graph name: " + data_type+str(serial_number))

            self.graph_names.append(data_type+str(serial_number))
            self.active_graphs.append(False)


        if "Windows" == platform.system():
            path_to_logo = "./src/icons/logo_n.bmp" # this is the window icon

        elif "Linux" == platform.system():
            path_to_logo = "./src/icons/logo_n.xbm" # this is the linux icon
            

        # this is for tinker configuration used by the file system dialog finder
        root = Tk()    
        root.withdraw() # this will hide a source tinker window
        abspath_to_logo = os.path.abspath(path_to_logo)
        print("the abspath_to_logo is: "+abspath_to_logo)
        root_file_dir = os.path.dirname(abspath_to_logo)
        print("the root file dir is: "+root_file_dir)


        # set up the plot objects on a vector and initialize them

        graph_widgets = (

            # energy metter:
            View.window.gw_energia1,
            View.window.gw_corriente1,
            View.window.gw_fp1,
            View.window.gw_energia2,
            View.window.gw_corriente2,
            View.window.gw_fp2,

            # flow metter  
            View.window.gw_volumen1,
            View.window.gw_flujo1,

            # confort metter
            View.window.gw_temperatura1,
            View.window.gw_humedad1,
            View.window.gw_temperatura2,
            View.window.gw_humedad2,
            View.window.gw_temperatura3,
            View.window.gw_humedad3,
            View.window.gw_temperatura4,
            View.window.gw_humedad4,
            View.window.gw_temperatura5,
            View.window.gw_humedad5,

        )

        self.plots = OrderedDict()
        
        for key, g_widget in enumerate(graph_widgets):
            print(">> the name of the graph is: "+self.graph_names[key]+" on the index: "+str(key))
            self.plots[self.graph_names[key]] = Plot2D(g_widget, self.graph_names[key])

        # set up the lcd 
        self.lcd_vec = (
            # energy metter:
            View.window.lcd_energia1,
            View.window.lcd_corriente1,
            View.window.lcd_fp1,
            View.window.lcd_energia2,
            View.window.lcd_corriente2,
            View.window.lcd_fp2,

            # flow metter  
            View.window.lcd_volumen1,
            View.window.lcd_flujo1,

            # confort metter
            View.window.lcd_temperatura1,
            View.window.lcd_humedad1,
            View.window.lcd_temperatura2,
            View.window.lcd_humedad2,
            View.window.lcd_temperatura3,
            View.window.lcd_humedad3,
            View.window.lcd_temperatura4,
            View.window.lcd_humedad4,
            View.window.lcd_temperatura5,
            View.window.lcd_humedad5,
        )

        ################################################################################
        #######--- define all the functions that calculate the next data point----######
        ################################################################################




        #-----------------energy metter 1--------------------
        def handler_energia1():
            
            plot_name = self.graph_names[0] # energia 1

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_energy, 1)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[0].display(new_value[0])
            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))
            
                
            
          

        def handler_corriente1():

            plot_name = self.graph_names[1] # corriente 1
            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_irms, 1)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[1].display(new_value[0])
            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))
                
            

        def handler_fp1():

            plot_name = self.graph_names[2] # factor de potencia 1
            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_fp, 1)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[2].display(new_value[0])
            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))

        #-----------------energy metter 2--------------------

        def handler_energia2():
            
            plot_name = self.graph_names[3] # energia 2
            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_energy, 2)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[3].display(new_value[0])

            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))

        def handler_corriente2():

            plot_name = self.graph_names[4] # corriente 2

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_irms, 2)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[4].display(new_value[0])

            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))

        def handler_fp2():

            plot_name = self.graph_names[5] # factor de potencia 2

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # to pass return from another thread
                future = executor.submit(self.View.controller.myModel.XbeeGrid.get_fp, 2)
                new_value = future.result()
                
            try:
                self.plots[plot_name].shift_value(new_value[0])
                self.lcd_vec[5].display(new_value[0])

            except Exception as e:
                print("avoiding to plot any further value in the screen"+plot_name+" "+str(e))

    
        #----------------- Flow metter 1--------------------

        def handler_volumen1():

            plot_name = self.graph_names[6] # fujo consumido 1

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = sin(2 * pi * new_time / 5) + sin(2 * pi * new_time * 43 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[1].display(new_value)

        def handler_flujo1():

            plot_name = self.graph_names[7] # flujo instantaneo 1

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = sin(2 * pi * new_time / 5) - sin(2 * pi * new_time * 3 / 5) + sin(2 * pi * new_time * 43/ 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[2].display(new_value)

        #----------------- confort metter 1--------------------

        def handler_temperatura1():

            plot_name = self.graph_names[8] # temperatura 1

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[3].display(new_value)

        def handler_humedad1():

            plot_name = self.graph_names[9] # humedad 1

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time * 20 / 5) + 2 * cos(2 * pi * new_time * 10 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[4].display(new_value)
        
        #----------------- confort metter 2--------------------

        def handler_temperatura2():

            plot_name = self.graph_names[10] # temperatura 2

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[3].display(new_value)

        def handler_humedad2():

            plot_name = self.graph_names[11] # humedad 2

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time * 20 / 5) + 2 * cos(2 * pi * new_time * 10 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[4].display(new_value)

        #----------------- confort metter 3--------------------

        def handler_temperatura3():

            plot_name = self.graph_names[12] # temperatura 3

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[3].display(new_value)

        def handler_humedad3():

            plot_name = self.graph_names[13] # humedad 3

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time * 20 / 5) + 2 * cos(2 * pi * new_time * 10 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[4].display(new_value)
    
        #----------------- confort metter 4--------------------

        def handler_temperatura4():

            plot_name = self.graph_names[14] # temperatura 4

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[3].display(new_value)

        def handler_humedad4():

            plot_name = self.graph_names[15] # humedad 4

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time * 20 / 5) + 2 * cos(2 * pi * new_time * 10 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[4].display(new_value)

        #----------------- confort metter 5--------------------

        def handler_temperatura5():

            plot_name = self.graph_names[16] # temperatura 5

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[3].display(new_value)

        def handler_humedad5():

            plot_name = self.graph_names[17] # humedad 5

            new_time = self.plots[plot_name].time_queue[-1] + self.plots[plot_name].sample_time
            new_value = cos(2 * pi * new_time * 20 / 5) + 2 * cos(2 * pi * new_time * 10 / 5)
            self.plots[plot_name].shift_value(new_value)
            self.lcd_vec[4].display(new_value)


        self.handler_vec = (
            # energy metter:
            handler_energia1,
            handler_corriente1,
            handler_fp1,
            handler_energia2,
            handler_corriente2,
            handler_fp2,

            # flow metter  
            handler_volumen1,
            handler_flujo1,

            # confort metter
            handler_temperatura1,
            handler_humedad1,
            handler_temperatura2,
            handler_humedad2,
            handler_temperatura3,
            handler_humedad3,
            handler_temperatura4,
            handler_humedad4,
            handler_temperatura5,
            handler_humedad5,
        )

        
        # connect all the buttons
        self.start_buttons = (
            # energy metter:
            View.window.start_energia1,
            View.window.start_corriente1,
            View.window.start_fp1,
            View.window.start_energia2,
            View.window.start_corriente2,
            View.window.start_fp2,

            # flow metter  
            View.window.start_volumen1,
            View.window.start_flujo1,

            # confort metter
            View.window.start_temperatura1,
            View.window.start_humedad1,
            View.window.start_temperatura2,
            View.window.start_humedad2,
            View.window.start_temperatura3,
            View.window.start_humedad3,
            View.window.start_temperatura4,
            View.window.start_humedad4,
            View.window.start_temperatura5,
            View.window.start_humedad5      
        )

        self.stop_buttons = (
            # energy metter:
            View.window.stop_energia1,
            View.window.stop_corriente1,
            View.window.stop_fp1,
            View.window.stop_energia2,
            View.window.stop_corriente2,
            View.window.stop_fp2,

            # flow metter  
            View.window.stop_volumen1,
            View.window.stop_flujo1,

            # confort metter
            View.window.stop_temperatura1,
            View.window.stop_humedad1,
            View.window.stop_temperatura2,
            View.window.stop_humedad2,
            View.window.stop_temperatura3,
            View.window.stop_humedad3,
            View.window.stop_temperatura4,
            View.window.stop_humedad4,
            View.window.stop_temperatura5,
            View.window.stop_humedad5,         
        )

        for index in range(len(self.start_buttons)):
            self.stop_buttons[index].clicked.connect(partial(self.on_stop, self.graph_names[index]))
            self.start_buttons[index].clicked.connect(partial(self.on_start, self.graph_names[index]))
        
        # connect all the bars

        self.sampleRate_sliders = (
            
            View.window.sampleRate_energia_slider1,
            View.window.sampleRate_corriente_slider1,
            View.window.sampleRate_fp_slider1,
            View.window.sampleRate_energia_slider2,
            View.window.sampleRate_corriente_slider2,
            View.window.sampleRate_fp_slider2,

            View.window.sampleRate_volumen_slider1,
            View.window.sampleRate_flujo_slider1,

            View.window.sampleRate_temperatura_slider1,
            View.window.sampleRate_humedad_slider1,
            View.window.sampleRate_temperatura_slider2,
            View.window.sampleRate_humedad_slider2,
            View.window.sampleRate_temperatura_slider3,
            View.window.sampleRate_humedad_slider3,
            View.window.sampleRate_temperatura_slider4,
            View.window.sampleRate_humedad_slider4,
            View.window.sampleRate_temperatura_slider5,
            View.window.sampleRate_humedad_slider5,            
        )

        self.points_sliders = (
            View.window.points_energia_slider1,
            View.window.points_corriente_slider1,
            View.window.points_fp_slider1,
            View.window.points_energia_slider2,
            View.window.points_corriente_slider2,
            View.window.points_fp_slider2,

            View.window.points_volumen_slider1,
            View.window.points_flujo_slider1,

            View.window.points_temperatura_slider1,
            View.window.points_humedad_slider1,
            View.window.points_temperatura_slider2,
            View.window.points_humedad_slider2,
            View.window.points_temperatura_slider3,
            View.window.points_humedad_slider3,
            View.window.points_temperatura_slider4,
            View.window.points_humedad_slider4,
            View.window.points_temperatura_slider5,
            View.window.points_humedad_slider5,             
        )

        for index in range(len(self.points_sliders)):
            self.sampleRate_sliders[index].valueChanged.connect(partial(self.on_sampleRate_changed, index))
            self.points_sliders[index].valueChanged.connect(partial(self.on_points_changed, index))

        # organize all the sample and points labels:
        self.sampleRate_labels = (
            View.window.sampleRate_energia_label1,
            View.window.sampleRate_corriente_label1,
            View.window.sampleRate_fp_label1,
            View.window.sampleRate_energia_label2,
            View.window.sampleRate_corriente_label2,
            View.window.sampleRate_fp_label2,

            View.window.sampleRate_volumen_label1,
            View.window.sampleRate_flujo_label1,

            View.window.sampleRate_temperatura_label1,
            View.window.sampleRate_humedad_label1,
            View.window.sampleRate_temperatura_label2,
            View.window.sampleRate_humedad_label2,
            View.window.sampleRate_temperatura_label3,
            View.window.sampleRate_humedad_label3,
            View.window.sampleRate_temperatura_label4,
            View.window.sampleRate_humedad_label4,
            View.window.sampleRate_temperatura_label5,
            View.window.sampleRate_humedad_label5,   
        )

            

        self.points_labels = (

            View.window.points_energia_label1,
            View.window.points_corriente_label1,
            View.window.points_fp_label1,
            View.window.points_energia_label2,
            View.window.points_corriente_label2,
            View.window.points_fp_label2,

            View.window.points_volumen_label1,
            View.window.points_flujo_label1,

            View.window.points_temperatura_label1,
            View.window.points_humedad_label1,
            View.window.points_temperatura_label2,
            View.window.points_humedad_label2,
            View.window.points_temperatura_label3,
            View.window.points_humedad_label3,
            View.window.points_temperatura_label4,
            View.window.points_humedad_label4,
            View.window.points_temperatura_label5,
            View.window.points_humedad_label5,   
        )

        # connect all the save buttons
        self.save_buttons = (
            
            View.window.save_energia1,
            View.window.save_corriente1,
            View.window.save_fp1,
            View.window.save_energia2,
            View.window.save_corriente2,
            View.window.save_fp2,

            # flow metter  
            View.window.save_volumen1,
            View.window.save_flujo1,

            # confort metter
            View.window.save_temperatura1,
            View.window.save_humedad1,
            View.window.save_temperatura2,
            View.window.save_humedad2,
            View.window.save_temperatura3,
            View.window.save_humedad3,
            View.window.save_temperatura4,
            View.window.save_humedad4,
            View.window.save_temperatura5,
            View.window.save_humedad5,
        )

        for index, save_bt in enumerate(self.save_buttons):
             save_bt.clicked.connect(partial(self.on_save, index))


    ##################################################################
    #######----------------- the object methods ----------------######
    ##################################################################

    def on_measure_selector(self, index):
        print(">>> the not(supposedly) index is: "+str(index))
        self.View.window.stackedMeasure.setCurrentIndex(index)

    def on_sampleRate_changed(self, index, new_value):
        #current_value = self.sampleRate_sliders[index].value() # this is a diferent way to get the slider value
        self.sampleRate_labels[index].setText("Sample Rate (hz): "+str(new_value))
        self.plots[self.graph_names[index]].set_new_timer(1000 / new_value)

    def on_points_changed(self, index, new_value):
        self.points_labels[index].setText("Number of poinst: "+str(new_value))
        self.plots[self.graph_names[index]].resize_plot(new_value)

    def on_start(self, graph_name):
        print("Start button pressed: "+graph_name)
        self.plots[graph_name].start(self.handler_vec[self.graph_names.index(graph_name)])
        self.active_graphs[self.graph_names.index(graph_name)] = True

    def on_stop(self, graph_name):
        print("stop button pressed: "+graph_name)
        self.plots[graph_name].stop()
        self.active_graphs[self.graph_names.index(graph_name)] = False

    def on_save(self, index):

        self.on_stop(self.graph_names[index])
        
        # get the time in a string format
        date_now = datetime.datetime.now()
        string_date, string_time = str(date_now).split(" ")
        string_time = string_time[:8] # remove the microseconds
        string_time = string_time.replace(":","~")

        # format the data for EXCEL
        file_name = self.graph_names[index]+"_"+string_date+"_"+string_time+'.csv'
        list_data = [
            ["time_stamp:"] + list(map(lambda item: str(item).replace(".", ","), np.array(self.plots[self.graph_names[index]].time_queue))),
            ["value:"] + list(map(lambda item: str(item).replace(".", ","), np.array(self.plots[self.graph_names[index]].value_queue)))
            ]
        list_data = np.transpose(list_data)
        print("data list: " + str(list_data))

        # format the paths
        user_home_path = expanduser("~")
        try:
            loaded_file = asksaveasfile(
                mode='w',
                initialdir = user_home_path,
                title="Save the data", 
                initialfile=file_name,
                defaultextension=".csv",
                filetypes= [
                    ('All Files', '*.*'),  
                    ('Coma separated values', '*.csv'), 
                    ('Text Document', '*.txt')
                    ],
            )
            full_file_path = loaded_file.name
            print("______the full directory is:"+full_file_path)
            loaded_file.close()            
        except IOError as e:
            print("error founded loading the file: "+str(e))
        
        # write the file
        with open(full_file_path, 'w', newline='') as loaded_file:
            writer = csv.writer(
                loaded_file, 
                dialect=csv.excel,
                delimiter=';', 
                #quotechar='"', 
                #quoting=csv.QUOTE_ALL
            )
            writer.writerows(list_data)
        
            


    