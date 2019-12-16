import datetime
import time
import json
from threading import Thread
import logging
logging.basicConfig(level=logging.DEBUG) # this will set all the debugging messages on

import copy 

import numpy as np

from MqttManager import MqttManager
# from httpManager import HttpManager

# this one is only for data storage
class RemoteDataManager(object):

    def __init__(self,  controller, config):
        
        self.myController = controller
        self.is_connected = False
        self.currentConfig = config

        self.myMqttManager = MqttManager(
            sql_uid=self.currentConfig["sql_uid"],
            on_control_callback = self.on_control_callback,
            on_measure_callback = self.on_measure_callback,
            on_disconnect_callback= self.disconected,
            on_connect_callback = self.connected,
        )
    
    
    def connected(self):
        self.myController.remote_mode = True
        self.myController.myView.window.remote_mode_button.setChecked(True)

    def disconected(self):
        self.myController.remote_mode = False
        self.myController.myView.window.remote_mode_button.setChecked(False)

    def send_controll_message(self, device_name_vec, serial_number_vec, data_type_vec, data_vec):
        # get the current date and time
        date_now = datetime.datetime.utcnow()
        (string_date, string_time) = str(date_now).split(" ")
        string_date_vec = list(np.full(4, string_date))
        string_time_vec = list(np.full(4, string_time))
        data_type_vec = ["circuito 1","circuito 2","circuito 3","circuito 4"]


        data_format = {
            "sql_uid": self.myMqttManager.sql_uid, 
            "mqtt_sub_folder": "control/app",
            "operation":"send-save",
            "message":{
                "device_names": device_name_vec,
                "serial_numbers": serial_number_vec,
                "data_types": data_type_vec,
                "data": data_vec,
                "date": string_date_vec,
                "time": string_time_vec,
            }
        }
        self.myMqttManager.publish_control(data_format)

    def send_measure_message(self, device_name_vec, serial_number_vec, data_type_vec, data_vec):

        # get the current date and time
        date_now = datetime.datetime.utcnow()
        (string_date, string_time) = str(date_now).split(" ")
        string_date_vec = list(np.full(len(data_vec), string_date))
        string_time_vec = list(np.full(len(data_vec), string_time))

        data_format = {
            "sql_uid": self.myMqttManager.sql_uid, 
            "mqtt_sub_folder": "measure/app",
            "operation":"send-save",
            "message":{
                "device_names": device_name_vec,
                "serial_numbers": serial_number_vec,
                "data_types": data_type_vec,
                "data": data_vec,
                "date": string_date_vec,
                "time": string_time_vec,
            }
        }

        self.myMqttManager.publish_measure(data_format)

    def on_control_callback(self, mqtt_message_dic):

        local_dic = copy.deepcopy(mqtt_message_dic) 

        data_types = list(local_dic["data_types"])
        serial_numbers = list(local_dic["serial_numbers"])
        data = list(local_dic["data"])

        circuit_list = copy.deepcopy( list(self.myController.myView.myControlScreen.circuits_name))

        print("inside controll callback")
        print(">> 1) the full buttons name "+str(circuit_list))
        #print("the full is: "+str(local_dic))
        #print("the data is: "+str(local_dic["data"]))
        print(">> 2) data types:"+str(data_types))
        print(">> 3) the serial numbers:"+str(serial_numbers))
        print(">> 4) the data list is: " +  str(data))

        i = 0

        

        for value in data:

            circuit_name = str(data_types[i])+"_"+str(serial_numbers[i])
            print(">> 5) circuit name activated: "+circuit_name)
            
            local_index = circuit_list.index(circuit_name)
            print(local_index)

            if value == "on":
                self.myController.myView.myControlScreen.set_circuit(local_index, on=True)
            elif value == "off":
                self.myController.myView.myControlScreen.set_circuit(local_index, on=False)
            else:
                print("data type not recognized: "+circuit_name)
            
            
            print(value)
            i += 1



    def on_measure_callback(self, mqtt_message_dic):
        pass

    """
    {
            "message":{
                "device_names": ["smart 1", "smart 2"],
                "serial_numbers": "1234",
                "data_types": ["circuito 1", "circuito 2"],
                "data": ["on", "off"],
                "date": ["21-23-11"],
                "time": ["do"]
            }
        }
    """

