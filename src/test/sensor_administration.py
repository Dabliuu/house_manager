

import time
import logging

import os
import subprocess

# import mysql.connector

import json

import controllers

class serial_comunication_protocol(object):
    pass
    @staticmethod
    def get_data(data_type):
        pass
        return []

    @staticmethod
    def set_data(data_type, *data):
        pass
        return True

__metaclass__ = type # needed for python 2.7 version compatibility


# this one is only for data storage
class Sensor(object):

    def __init__(self,  **sensor_charateristics):
        self.device_name = []
        self.memory_data = [] # list of tuples
        self.data_types = []
        self.serial_number = []
        for characteristic, value in sensor_charateristics.items():
            if characteristic == 'data-types':
                self.data_types = value        # list of data types strings
            if characteristic == 'serial-number':
                self.serial_number = value  # string number
            if characteristic == 'device-name':
                self.device_name = value   #database string name

    def __repr__(self):
        return str(self.device_name)+"__"+str(self.serial_number)


def is_connected_to_http():
    return True

def is_connected_to_mqtt():
    return True

class MedidorElectricoUV (Sensor):
    characteristics = {
        'device-name': 'Medidor Electrico UV 2.0',
        'serial-number': None,  # 0000000001
        'data-type-name': ['Voltaje DC', 'Corriente DC', 'Voltaje AC', 'Corriente AC']
    }

    def __init__(self, serial_number):
        self.characteristics = MedidorElectricoUV.characteristics
        self.characteristics['serial-number'] = serial_number
        super(MedidorElectricoUV, self).__init__(**self.characteristics)  # initialize the parent Sensor

    def get_measure_data(self, data_type):
        data = None
        try:
            # check if the data type exist
            self.data_types.index(data_type)
            # get the data from the comunication protocol object into a list:
            data = serial_comunication_protocol().get_data(data_type)
        except Exception:
            logging.debug("wrong arguments")
        return data

    def set_control_data(self, data_type, *data):
        done = False
        try:
            # check if the data type exist
            self.data_types.index(data_type)
            # set the data_type register using the comunication protocol:
            done = serial_comunication_protocol().set_data(data_type, data)
        except Exception:
            logging.debug("wrong arguments")
        return done


class MedidorDeConfortUV (Sensor):
    characteristics = {
        'device-name': 'Medidor De Confort UV 2.0',
        'serial-number': None,  # 4000000001,
        'data-type-name': ['humedad relativa', 'temperatura']
    }
    def __init__(self, serial_number):
        self.characteristics = MedidorDeConfortUV.characteristics
        self.characteristics['serial-number'] = serial_number
        super(MedidorDeConfortUV, self).__init__(**self.characteristics)  # initialize the parent Sensor

    def get_measure_data(self, data_type):
        data = None
        try:
            # check if the data type exist
            self.data_types.index(data_type)
            # get the data from the comunication protocol object into a list:
            data = serial_comunication_protocol().get_data(data_type)
        except Exception:
            logging.debug("wrong arguments")
        return data

    def set_control_data(self, data_type, *data):
        done = False
        try:
            # check if the data type exist
            self.data_types.index(data_type)
            # set the data_type register using the comunication protocol:
            done = serial_comunication_protocol().set_data(data_type, data)
        except Exception:
            logging.debug("wrong arguments")
        return done


class ElectricControllerGrid (Sensor):
    characteristics = {
        'device-name': 'Electric Controller Grid 1.0',
        'serial-number': None,  # 1000000001,
        'data-type-name': ['control circuito a', 'control circuito b', 'control circuito c',
                           'control circuito d'
                           'medicion circuito A', 'medicion circuito b', 'medicion circuito c',
                           'medicion circuito d']
    }

    def __init__(self, serial_number):
        self.characteristics = ElectricControllerGrid.characteristics
        self.characteristics['serial-number'] = serial_number
        super(ElectricControllerGrid, self).__init__(**self.characteristics)  # initialize the parent Sensor


class MyDbManager:

    def __init__(self, my_model):

        self.my_model = my_model

        self.remote_config = {
            'user': 'root',
            'password': 'juandara_b9a842',
            'database': 'iot_db',
            'host': '35.231.241.254',  # Google sql server static ip
            'port': '3306',  # TCP/IP port,
            # 'client_flags': [ClientFlag.SSL],  # flag for enabling ssl connection
            'ssl_ca': './certificates/server-ca.pem',
            'ssl_cert': './certificates/client-cert.pem',
            'ssl_key': './certificates/client-key.pem',
            'ssl_verify_cert': 'True',
            # 'connection_timeout': 86400  # 86400 seconds for timeout (1 day)
            'use_pure': 'True'
            # "unix_socket" : "addresssd\sdas"
        }
        self.local_config = {
            'user': 'root',
            'password': 'juandara_b9a842',
            'database': 'iot_db',
            'host': '127.0.0.1'  # localhost
        }
        self.remote_mode = True
        self.configuration = self.remote_config

        # the conection verifier allow me to check the
        self.connection_verifier = controllers.RepeatedTimer(10, self.conn_verifier_routine)  # verify every minute
        self.connection_verifier.stop()  # it is asumed that the connection is remote at fist

    # for internal database mode administration:
    def conn_verifier_routine(self):
        try:
            print("verifying connection:")
            if is_connected_to_http() and is_connected_to_mqtt():
                print("remote server online")
                self.to_remote_mode(True)
        except Exception as err:
            print("remote server stil offline: ")
            print(err)
            self.to_remote_mode(False)

        if self.remote_mode:
            self.my_model.controller.myView.window.remote_mode.setChecked(True)
        else:
            self.my_model.controller.myView.window.remote_mode.setChecked(False)

    # to change the mode of the database operation
    def to_remote_mode(self, yes):
        if yes:
            print("remote on")
            self.configuration = self.remote_config
            self.remote_mode = True

            #self.connection_verifier.stop()
        else:
            print("local on")
            self.remote_mode = False
            self.configuration = self.local_config
            #self.connection_verifier.start()

    # use the configuration file to write the basic structure of the local db
    def configure_local_db(self):
       logging.debug("configuring the local db")

    # conect to REMOTE server to get a list of devices subscribed
    def get_devices(self, current_place):
        logging.debug("getting sensors and actuators attached to the rasp")
        sensors = ["water","electricity"]
        return sensors

    #  ------- to procces data in the current server:-------
    def insertSensorData(self, sensor, *data):
        logging.debug("save data to the system")
        done = True
        return done

    def selectSensorData(self, sensor, max_day="3000-01-30", min_day="1000-01-30"):
        logging.debug("getting the data from the system")
        data = []
        return data

    def update_controllable_data(self, sensor, *data):
        pass

    def backUpAllSensorData(self, sensors):
        pass


class Model:

    def __init__(self, controller):

        self.controller = controller

        # initialize de databases managers objects:
        self.myDatabaseManager = MyDbManager(self)  # the default value is True

        #  initialize the basic manager information:
        self.current_user = ""
        self.center_name = ""
        self.mySensors = []

        # reload the configuration (sensors and center name) file from a JSON file
        self.reload_configuration_from_file()

        #self.myDatabaseManager.configure_local_db()

        print("model init done!")

    def init_sensors(self, *sensor_identification_pair_list):

        for eachSensor in sensor_identification_pair_list:

            logging.debug(eachSensor)

            if eachSensor[0] == MedidorElectricoUV.characteristics['device-name']:  # name
                self.mySensors.append(MedidorElectricoUV(eachSensor[1])) # serial number

            elif eachSensor[0] == MedidorDeConfortUV.characteristics['device-name']:
                self.mySensors.append(MedidorDeConfortUV(eachSensor[1]))

            elif eachSensor[0] == ElectricControllerGrid.characteristics['device-name']:
                self.mySensors.append(ElectricControllerGrid(eachSensor[1]))
            else:
                logging.debug("initialization error, sensor name not name found")

    def reload_configuration_from_file(self):
        myList = []
        try:
            # read and get the configuration from the file
            with open('config.json') as json_data_file:
                data = json.load(json_data_file)
                logging.debug(data)  # now this becomes a dictionary with unicode string formats

            #  proces de json file data:
            self.center_name = data["center_name"]
            self.current_user = data["e_mail"]
            for sensor_dic in data["my_sensors"]:
                myList.append((str(sensor_dic["device_name"]), str(sensor_dic["serial_number"])))
        except Exception as e:
            logging.debug("generic error wile reloading the configuration file: ")
            print(e)

        # initialize every sensor:
        self.init_sensors(*myList)  # pair tuple list

    def write_configuration_file(self):

        data = {}
        # it should exist a routine function to get the e mail form the json file gathered form the credentials
        # data['e_mail'] = self.controller.myView.window.center_name.text()
        data['e_mail'] = "juan.ramirez.villegas@correounivalle.edu.co"
        # data['center_name'] = self.center_name
        data['center_name'] = "ViviendaSolarDecathlon"

        devices_tup = self.myDatabaseManager.get_devices(data['center_name'])

        data['my_sensors'] = []
        for sensor in devices_tup:
            data['my_sensors'].append({
                'device_name': sensor[0],
                'serial_number': sensor[1]
            })

        with open('config.json', 'w') as outfile:
            json.dump(data, outfile)

    def autenticate_user(self):
        Model.comand_with_response("gcloud auth application-default login", "y")  # the yes is needed for still creating
        # the auth given the fact that the eviromental variable is set
        # self.auth_path = default_auth_path = "C:\Users\USER\AppData\Roaming\gcloud\\application_default_credentials.json"

    @staticmethod
    def comand_with_response(comand, *responses):
        logging.debug("executing comand:"+comand)
        p = subprocess.Popen(comand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        newline = os.linesep  # this is the object that handles the comunication
        logging.debug("responses handled: "+responses)
        p.communicate(newline.join(responses))
        logging.debug("done")