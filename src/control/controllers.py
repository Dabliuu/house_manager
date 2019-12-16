import sys



import threading
import time
import logging
import csv
import os
from os.path import expanduser

import datetime
import socket

import webbrowser
import json
import numpy as np


from RepeatedTimer import RepeatedTimer 
from RemoteDataManager import RemoteDataManager


FULL_DESKTOP_PATH = expanduser("~")


def get_index_from_object_list(list, representation):
    for index, item in enumerate(list):
        if item.__repr__() == representation:
            logging.debug(index)
            return index
    return None

class Controller:

    def __init__(self, config):

        self.backup_interval = 20
        self.next_backup_time = time.time() + self.backup_interval  # back up cada media hora

        self.myView = None
        self.myModel = None
        self.myRemote = None
        self.currentConfig = config
        
        self.remote_mode = False
        self.create_manager = True
        self.try_connection = True

        # inicialize the individual sub program controllers
        # self.sd_controller = RepeatedTimer(10, self.sd_controller_routine)

        print("controller init done!")

    def report_handler(self):

        
        logging.basicConfig(level=logging.DEBUG) # this will set all the debugging messages on
        logging.debug("reporting handler started... current mode: "+str(self.remote_mode))
        
        device_name_vec = list()
        
        
        serial_number_vec = list()
        
        
        data_type_vec = list()
        
        
        
        data_vec = list()
        
        is_reportable_data = False
        # procces all the masured data, only if the graph is active:
        mScreen = self.myView.myMeasureScreen
        # print("---->>> the screen plots: "+str(mScreen.plots))
        for index, graph_name in enumerate(mScreen.plots): # process a dictionary
            if mScreen.active_graphs[index]:
                dataQueue = mScreen.plots[graph_name].value_queue
                dataValue = np.array(dataQueue)[-1] #get the last value
                #print("---->>> vec temperature queue value: "+str(dataQueue))
                print("---->>> Uploaded "+ str(dataValue)+" of: "+graph_name)

                device_name_vec += [ self.currentConfig["device_names"][index] ]
                serial_number_vec += [ self.currentConfig["serial_numbers"][index] ]
                data_type_vec += [ self.currentConfig["data_types"][index] ]
                data_vec += [dataValue]

                is_reportable_data=True

        # only if there is active plots save the data
        if is_reportable_data:

            # if a connection was made
            if self.remote_mode and self.try_connection:
                if self.create_manager:
                    self.remote_mode = True
                    self.myView.window.remote_mode_button.setChecked(True)  

                    self.myRemote = RemoteDataManager(self, self.currentConfig)
                    self.create_manager=False
                
                self.myRemote.send_measure_message(device_name_vec, serial_number_vec, data_type_vec, data_vec)
            else:
                # test connection and retry schedule
                if self.is_internet() and self.try_connection:
                    try:
                        # self.myRemote = RemoteDataManager(self, self.currentConfig)
                        self.remote_mode = True
                        self.myView.window.remote_mode_button.setChecked(True)  
                        logging.debug('Now on remote mode')
                        
                        
                        self._timer = threading.Timer(self.currentConfig["report_rate"],  self.report_handler)
                        self._timer.start()

                    except IOError:
                        self.myRemote.disconnected()

                # save to hard disk
                else:
                    #logging.debug('Now on local mode')
                    self.remote_mode = False
                    self.myView.window.remote_mode_button.setChecked(False)

                    # get the time in a string format
                    date_now = datetime.datetime.now()
                    [string_date, string_time]  = str(date_now).split(" ")

                    # prepare the vectors to write to the file
                    string_date_vec = list(np.full(len(data_vec), string_date))
                    string_time_vec = list(np.full(len(data_vec), string_time))
                    
                    multi_row = [
                        string_time_vec, 
                        data_type_vec, 
                        list(map(lambda data_item: str(data_item).replace(".", ","), data_vec))
                    ]

                    # format the data 
                    file_name = "Data"+"_"+string_date+'.csv'
                    full_path = FULL_DESKTOP_PATH+"\\"+file_name

                    print("saving data to hard disk: "+full_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'a',  newline='') as csvFile:
                            writer = csv.writer(
                                csvFile,
                                dialect=csv.excel,
                                delimiter=';'
                                )
                            writer.writerows([*zip(*multi_row)]) # transpond work arround without numpy
                    else:
                        with open(full_path, 'w', newline='') as csvFile:
                            writer = csv.writer(
                                csvFile,
                                dialect=csv.excel,
                                delimiter=';'
                                )
                            writer.writerow(["Time of adquisition","Data type","Data adquired"])

        # if there is not data available update the mode
        elif self.try_connection and self.is_internet():
            
            # update the state of the connection
            self.remote_mode = True
            self.myView.window.remote_mode_button.setChecked(True)
        else:
            self.remote_mode = False
            self.myView.window.remote_mode_button.setChecked(False)

        
    

        # this is a delayed thread to handle the remote mode:
        self._timer = threading.Timer(
            interval= self.currentConfig["report_rate"],
            function = self.report_handler
        )
        # self._timer.setDaemon(True)
        self._timer.start()

    def report_controlled(self, circuit_index):

        # here should be logic to handle multiple request in one  with a buffer and a timeout

        if self.remote_mode:
            
            pressed_button = self.myView.myControlScreen.circuits_obj[circuit_index]
            data_vec = list()

            if pressed_button.isChecked():
                data_vec+=["on"]
            else:
                data_vec+=["off"]

            self.myRemote.send_controll_message(
                ["Control grid SDL"], 
                [self.currentConfig["control__serial_numbers"][circuit_index] ],
                [self.currentConfig["control__data_types"][circuit_index] ],
                data_vec
            )

    
    def is_internet(self, host="www.google.com", port=80, timeout=3):
      """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("----- internet connection ok")
        return True
      except socket.error as ex:
        print ("----- internet connection failed: " + str(ex))
        return False

    def add_view_model(self, view, model):
        self.myView = view
        self.myModel = model


        # test connection and retry schedule
        try:
            self.remote_mode=True
            self.create_manager = False
            self.myRemote = RemoteDataManager(self, self.currentConfig)
            logging.debug('Now on remote mode')
        except IOError:
            self.remote_mode = False
            self.create_manager = True

       # this is a delayed thread to handle the remote mode:
        myBackgroundTimer = threading.Timer(
            interval=5,
            function = self.report_handler
        )
        myBackgroundTimer.setDaemon(True)
        myBackgroundTimer.start()

        
       
        


    def open_facebook(self):
        webbrowser.open('http://www.facebook.com')

