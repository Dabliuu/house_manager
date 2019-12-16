import time
import logging
import threading
from functools import partial
import json
from datetime import timedelta  
import csv
import datetime
from tkinter.filedialog import asksaveasfile
from tkinter import Tk
import os 
from os.path import expanduser

from BackgroundTimer import BackgroundTimer
from Plot2D import Plot2D

import numpy as np
from numpy import pi, sin, cos, tan
from PyQt5 import QtGui

class ConfigScreen():

    def __init__(self, View, config):

        self.View = View
        self.current_config = config

        # define the basic visual objects
        self.config_sliders = (
            View.window.cost_kwh,
            View.window.cost_m3,
            View.window.notification_day, 
            View.window.report_rate
        )

        self.config_sliders_labels = (
            View.window.cost_kwh_label,
            View.window.cost_m3_label,
            View.window.notification_day_label, 
            View.window.report_rate_label
        )

        self.config_sliders_names = (
            "cost_kwh",
            "cost_m3",
            "notification_day",
            "report_rate"
        )

        self.labels = (
            "Cost of kwh in COP: ",
            "Cost of m^3 of water in COP: ",
            "Notification day: ",
            "Report data rate in seconds: "
        )

        self.config_check_box = (
            View.window.email_notifications,
            View.window.remote_mode_button
        )

        self.config_check_box_names = (
            "email_notifications",
            "remote_mode"
        )

        # load the configuration from the json file
        self.load_config_data()

        # relate the handler for sliders and the check boxes
        for index, slider in enumerate(self.config_sliders):
            slider.valueChanged.connect(partial(self.on_slider_changed, index))
        
        for index, check_box in enumerate(self.config_check_box):
            check_box.clicked.connect(partial(self.on_check_changed, index))

        # connect all the buttons to the clicked handler:
        View.window.default_config.clicked.connect(self.default_config)
        View.window.save_config.clicked.connect(self.save_config)

    def change_db_mode(self):
        print("change_mode_check pressed")
        if self.View.window.remote_mode_button.isChecked():
            self.View.window.remote_mode_button.setChecked(True)
            self.View.controller.try_connection = True
        else:
            self.View.window.remote_mode_button.setChecked(False)
            self.View.controller.try_connection = False

    def load_config_data(self):

        """
        # load the configuration file:
        try:
            # read and get the configuration from the file
            with open("./config.json") as json_data_file:
                self.current_config = json.load(json_data_file)
                logging.debug(self.current_config)  # now this becomes a dictionary with unicode string formats

        except Exception as e:
            logging.debug("generic error wile reloading the configuration file: ")
            print(e)
        """

        # set all visual objecs to the loaded values
        self.View.window.cost_kwh.setValue(self.current_config["cost_kwh"])
        self.config_sliders_labels[0].setText(self.labels[0]+str(self.current_config["cost_kwh"]))
        self.View.window.cost_m3.setValue(self.current_config["cost_m3"])
        self.config_sliders_labels[1].setText(self.labels[1]+str(self.current_config["cost_m3"]))
        self.View.window.notification_day.setValue(self.current_config["notification_day"])
        self.config_sliders_labels[2].setText(self.labels[2]+str(self.current_config["notification_day"]))
        self.View.window.report_rate.setValue(self.current_config["report_rate"])
        self.config_sliders_labels[3].setText(self.labels[3]+str(self.current_config["report_rate"]))
        
        if self.current_config["email_notifications"] == "on": self.config_check_box[0].setChecked(True)
        else: self.config_check_box[0].setChecked(False)
        if self.current_config["remote_mode"] == "on": self.config_check_box[1].setChecked(True)
        else: self.config_check_box[1].setChecked(False)


    def on_slider_changed(self, index, new_value):
        #current_value = self.sampleRate_sliders[index].value() # this is a diferent way to get the slider value
        self.config_sliders_labels[index].setText(self.labels[index]+str(new_value))
        self.current_config[self.config_sliders_names[index]] = new_value

    def on_check_changed(self, index):
        if self.config_check_box[index].isChecked():
            self.current_config[self.config_check_box_names[index]] = "on"
        else:
            self.current_config[self.config_check_box_names[index]] = "off"

        if self.config_check_box[index] == self.View.window.remote_mode_button:
            self.change_db_mode()


    def save_config(self):
        
        with open('./config.json', 'w') as outfile:
            json.dump(self.current_config, outfile)

        #display a message
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Configuration correctly saved")
        msgBox.setWindowTitle("¡Hi!")
        ret = msgBox.exec_() 

    def default_config(self):
      
        # ram update
        self.current_config["cost_kwh"] = 500
        self.current_config["cost_m3"] = 300
        self.current_config["notification_day"] = 15 
        self.current_config["report_rate"] = 10
        self.current_config["email_notifications"] = "on"
        self.current_config["remote_mode"] = "off"


        # self.current_config["serial_number"] = 1000000000
        self.current_config["device_names"] = [
            
            # potencia
            "Energy Metter SDL",
            "Energy Metter SDL",
            "Energy Metter SDL",
            "Energy Metter SDL",
            "Energy Metter SDL",
            "Energy Metter SDL",

            # fluido
            "Flow Metter SDL",
            "Flow Metter SDL",

            # Confort
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL",
            "Confort Metter SDL"
        ]

        self.current_config["data_types"] = [
            
            # potencia
            "potencia acumulada",
            "corriente instantenea",
            "factor de potencia",
            "potencia acumulada",
            "corriente instantenea",
            "factor de potencia",

            # fluido
            "fluido consumido",
            "flujo instantaneo",

            # Confort
            "temperatura",
            "humedad",
            "temperatura",
            "humedad",
            "temperatura",
            "humedad",
            "temperatura",
            "humedad",
            "temperatura",
            "humedad"
        ]

        self.current_config["serial_numbers"] = [
            
            # potencia
            1,
            1,
            1,
            2,
            2,
            2,
            
            # fluido
            1,
            1,

            # Confort
            1,
            1,
            2,
            2,
            3,
            3,
            4,
            4,
            5,
            5
        ]

        self.current_config["xbee_names"] = [
            
            "EM_1",
            "EM_1",
            "EM_1",
            "EM_2",
            "EM_2",
            "EM_2",

            "WM",
            "WM",

            "CM_1",
            "CM_1",
            "CM_2",
            "CM_2",
            "CM_3",
            "CM_3",
            "CM_4",
            "CM_4",
            "CM_5",
            "CM_5"
        ] 

        self.current_config["xbee_headers"] = [
            
            bytearray("E", "utf-8"),
            bytearray("I", "utf-8"),
            bytearray("FP", "utf-8"),
            bytearray("E", "utf-8"),
            bytearray("I", "utf-8"),
            bytearray("FP", "utf-8"),

            bytearray("WA", "utf-8"),
            bytearray("F", "utf-8"),

            bytearray("T", "utf-8"),
            bytearray("H", "utf-8"),
            bytearray("T", "utf-8"),
            bytearray("H", "utf-8"),
            bytearray("T", "utf-8"),
            bytearray("H", "utf-8"),
            bytearray("T", "utf-8"),
            bytearray("H", "utf-8"),
            bytearray("T", "utf-8"),
            bytearray("H", "utf-8")

        ]

        
        self.current_config["control__device_names"] = [

            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",

            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",

            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",

            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL",
            "Control grid SDL"

        ]

        self.current_config["control__serial_numbers"] = [

            1,
            1,
            1,
            1,

            2,
            2,
            2,
            2,

            3,
            3,
            3,
            3,

            4,
            4,
            4,
            4

        ]

        self.current_config["control__data_types"] = [

            "circuit1",
            "circuit2",
            "circuit3",
            "circuit4",

            "circuit1",
            "circuit2",
            "circuit3",
            "circuit4",

            "circuit1",
            "circuit2",
            "circuit3",
            "circuit4",

            "circuit1",
            "circuit2",
            "circuit3",
            "circuit4"

        ]


        #file update
        self.save_config()

        #visualy update
        self.load_config_data()

        #display a message
        #display a message
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Default configuration restored")
        msgBox.setWindowTitle("¡Hi!")
        ret = msgBox.exec_() 