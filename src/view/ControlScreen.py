
import time
import logging
import threading
from functools import partial
import json
from datetime import timedelta  
from threading import Thread

import datetime
from BackgroundTimer import BackgroundTimer
from custom_email import send_email

import pyqtgraph as pg

import copy 
import concurrent.futures

class ControlScreen():
    def __init__(self, View):

        self.View = View
        self.current_schedule = dict()
        self.email_sended = False

        # configure the control selector (combo box)
        self.View.window.control_selector.currentIndexChanged.connect(self.on_control_selector)


        # ------------------calendar seccion---------------
        self.calendars_obj = (
            View.window.circuit1_calendar1,
            View.window.circuit2_calendar1,
            View.window.circuit3_calendar1,
            View.window.circuit4_calendar1,

            View.window.circuit1_calendar2,
            View.window.circuit2_calendar2,
            View.window.circuit3_calendar2,
            View.window.circuit4_calendar2,

            View.window.circuit1_calendar3,
            View.window.circuit2_calendar3,
            View.window.circuit3_calendar3,
            View.window.circuit4_calendar3,

            View.window.circuit1_calendar4,
            View.window.circuit2_calendar4,
            View.window.circuit3_calendar4,
            View.window.circuit4_calendar4
        )
        # connect all the calendars to the clicked handler
        for index, calendars in enumerate(self.calendars_obj):
            calendars.clicked.connect(partial(self.calendar_clicked, index))
        
        # ----------------time edit seccion----------------

        self.off_time_obj = (
            View.window.circuit1_offTime1,
            View.window.circuit2_offTime1,
            View.window.circuit3_offTime1,
            View.window.circuit4_offTime1,

            View.window.circuit1_offTime2,
            View.window.circuit2_offTime2,
            View.window.circuit3_offTime2,
            View.window.circuit4_offTime2,

            View.window.circuit1_offTime3,
            View.window.circuit2_offTime3,
            View.window.circuit3_offTime3,
            View.window.circuit4_offTime3,

            View.window.circuit1_offTime4,
            View.window.circuit2_offTime4,
            View.window.circuit3_offTime4,
            View.window.circuit4_offTime4
        )

        # connect all the time selectes to the clicked handler
        for index, off_time in enumerate(self.off_time_obj):
            off_time.editingFinished.connect(partial(self.time_edit_pressed, index, "off"))

        self.on_time_obj = (
            View.window.circuit1_onTime1,
            View.window.circuit2_onTime1,
            View.window.circuit3_onTime1,
            View.window.circuit4_onTime1,

            View.window.circuit1_onTime2,
            View.window.circuit2_onTime2,
            View.window.circuit3_onTime2,
            View.window.circuit4_onTime2,

            View.window.circuit1_onTime3,
            View.window.circuit2_onTime3,
            View.window.circuit3_onTime3,
            View.window.circuit4_onTime3,

            View.window.circuit1_onTime4,
            View.window.circuit2_onTime4,
            View.window.circuit3_onTime4,
            View.window.circuit4_onTime4,
        )

        # connect all the time selectes to the clicked handler
        for index, on_time in enumerate(self.on_time_obj):
            on_time.editingFinished.connect(partial(self.time_edit_pressed, index, "on"))

        #-----------------------buttons seccion:-------------------------
        self.circuits_obj = (
            View.window.circuit1_button1, 
            View.window.circuit2_button1, 
            View.window.circuit3_button1, 
            View.window.circuit4_button1,

            View.window.circuit1_button2, 
            View.window.circuit2_button2, 
            View.window.circuit3_button2, 
            View.window.circuit4_button2,

            View.window.circuit1_button3, 
            View.window.circuit2_button3, 
            View.window.circuit3_button3, 
            View.window.circuit4_button3,

            View.window.circuit1_button4, 
            View.window.circuit2_button4, 
            View.window.circuit3_button4, 
            View.window.circuit4_button4

        )
        # connect all the buttons to the clicked handler:
        for index, buttons in enumerate(self.circuits_obj):
            buttons.clicked.connect(partial(self.button_clicked, index))


        # create the circuits identifier vector from the serial number and the active graphs helper

        self.circuits_name = list()
        self.schedule_enable = list()

        for index, data_type in enumerate(self.View.currentConfig["control__data_types"]):

            serial_number = self.View.currentConfig["control__serial_numbers"][index]
            print("--->>> Control Screen, control name: " + data_type+"_"+str(serial_number))

            self.circuits_name.append(str(data_type)+"_"+str(serial_number))
            self.schedule_enable.append(True)


        self.weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

        # load the schedule object (in python it becomes a dictionary)
        try:
            # read and get the configuration from the file
            with open("./src/view/schedule.json") as json_data_file:
                self.current_schedule = json.load(json_data_file)
                # logging.debug("the current schedule is: "+self.current_schedule)  # now this becomes a dictionary with unicode string formats

        except Exception as e:
            print("generic error wile reloading the schedule file: "+ e)

        # this is a helper class that creates a daemon thread that runs the function every
        # self.myBackgroundTimer = BackgroundTimer(self.schedule_handler, 10)
        # self.myBackgroundTimer.start()
        myBackgroundTimer = Thread(
            target = self.schedule_handler,
            daemon = True
        )
        myBackgroundTimer.start()

    def on_control_selector(self, index):
        print(">>> the not(supposedly) index is: "+str(index))
        self.View.window.stackedControl.setCurrentIndex(index)

    #----------------- calendar handling ----------------------
    def time_edit_pressed(self, calendar_index, p_type):
        
        if p_type == "on":
            time = self.on_time_obj[calendar_index].time().toString("hh:mm:ss")
            print("on time modified to: "+time)

            # write the new date to ram:
            week_day = self.calendars_obj[calendar_index].selectedDate().dayOfWeek()-1
            print("day is: "+str(week_day))
            self.current_schedule[self.circuits_name[calendar_index]][str(week_day)]["onTime"] = time
            print(str(self.current_schedule))
            

        elif p_type == "off":
            time = self.off_time_obj[calendar_index].time().toString("hh:mm:ss")
            print("off time modified to: "+time)

            # write the new date to ram:
            week_day = self.calendars_obj[calendar_index].selectedDate().dayOfWeek()-1
            print("day is: "+str(week_day))
            self.current_schedule[self.circuits_name[calendar_index]][str(week_day)]["offTime"] = time
        else:
            return

        # write the new date to disk
        try:
            # read and get the configuration from the file
            with open("./src/view/schedule.json", "w") as json_data_file:
                json.dump(self.current_schedule, json_data_file)
                # logging.debug(self.current_schedule)  # now this becomes a dictionary with unicode string formats

        except Exception as e:
            logging.debug("generic error wile reloading the configuration file: "+e)


    def calendar_clicked(self, calendar_index, date_pressed):

        # get the day of the week and check the current configuration in ram:
        week_day = date_pressed.dayOfWeek()-1
        on_time_touple = self.current_schedule[self.circuits_name[calendar_index]][str(week_day)]["onTime"].split(":")
        off_time_touple = self.current_schedule[self.circuits_name[calendar_index]][str(week_day)]["offTime"].split(":")

        #set the holders to the respectiva time
        self.on_time_obj[calendar_index].setTime(pg.QtCore.QTime(
            int(on_time_touple[0]),
            int(on_time_touple[1]),
            int(on_time_touple[2])
        ))
        self.off_time_obj[calendar_index].setTime(pg.QtCore.QTime(
            int(off_time_touple[0]),
            int(off_time_touple[1]),
            int(off_time_touple[2])
        ))
        
        # date = self.calendars_obj[calendar_index].selectedDate() # get the selected day of the calendar
        print("pressed day: "+str(week_day))
        print("selected date: "+str(date_pressed.toString("dd-MM-yyyy")))

    

    # -----------------direct button handling -----------------

    def button_clicked(self, circuit_index):
        print("change_mode_check pressed by: "+self.circuits_name[circuit_index])        
        if self.circuits_obj[circuit_index].isChecked():
            print("manual on")
            self.set_circuit(circuit_index, on=True) # turn of the circuit
            self.stop_schedule_for_24hrs(circuit_index) # turn off the schedule for 24 hours
            #self.circuits_obj[circuit_index].setChecked(False) # display the change on the view
        else:
            print("manual off")
            self.set_circuit(circuit_index, on=False)# turn of the circuit
            self.stop_schedule_for_24hrs(circuit_index) # turn off the schedule for 24 hours
        
        self.View.controller.report_controlled(circuit_index)

    def stop_schedule_for_24hrs(self, circuit_index):
        self.schedule_enable[circuit_index] = False
        fixer = threading.Timer(86400, set_True, args=(self.schedule_enable, circuit_index))
        fixer.setDaemon(True)
        fixer.start()


    def set_circuit(self, circuit_index, on=False):
        
        serial = int(self.circuits_name[circuit_index][-1])-1

        help_vec = [
            "circuit1",
            "circuit2",
            "circuit3",
            "circuit4"
        ]
        circuit_num = 1+help_vec.index(self.circuits_name[circuit_index][0:-2])

        #print("--->>>> serial number:"+str(serial))
        #print("--->>>> circuit_num:"+str(circuit_num))


        if on:
            
            self.View.controller.myModel.XbeeGrid.set_circuit(True, serial, circuit_num)
                 

            logging.debug("circuit: "+self.circuits_name[circuit_index]+" is on")
            self.circuits_obj[circuit_index].setChecked(True) # display the change on the view
        
        else:

            self.View.controller.myModel.XbeeGrid.set_circuit(False, serial, circuit_num)    

            logging.debug("circuit: "+self.circuits_name[circuit_index]+" is off")
            self.circuits_obj[circuit_index].setChecked(False) # display the change on the view

    
    # -----------------background function -----------------


    def schedule_handler(self):
        
        print("inside loop")
        # now info
        date_now = datetime.datetime.now()
        string_time_now = str(date_now).split(" ")[1]
        string_time_touple = string_time_now[:8].split(":")
        time_now = datetime.time(int(string_time_touple[0]), int(string_time_touple[1]), int(string_time_touple[2]))
        week_day = date_now.weekday() # this comes as an integer

        # check if its time to send email
        if self.View.currentConfig["email_notifications"] == "on":
            today_number = date_now.day
            if not self.email_sended and today_number == self.View.currentConfig['notification_day']:
                send_email(
                    electric = {"cost":self.View.currentConfig['cost_kwh'], "value": 234.234},
                    water = {"cost":self.View.currentConfig['cost_m3'], "value":300.4},
                    email = self.View.currentConfig['e_mail']
                )
                self.email_sended = True
            elif  today_number != self.View.currentConfig['notification_day']:
                self.email_sended = False

        # the saved info:
        #self.current_schedule['circuit1']["0"]["onTime"] # monday on time

        for index, circuit in enumerate(self.circuits_name):
            if self.schedule_enable[index]:
                
                # get the on time as a time object
                on_time_touple = self.current_schedule[circuit][str(week_day)]["onTime"].split(":")
                on_time = datetime.time(int(on_time_touple[0]), int(on_time_touple[1]), int(on_time_touple[2]))
                off_time_touple = self.current_schedule[circuit][str(week_day)]["offTime"].split(":")
                off_time = datetime.time(int(off_time_touple[0]), int(off_time_touple[1]), int(off_time_touple[2]))

                # modify the button
                if off_time <= on_time: # if off band -----___-----
                    print("off band mode")
                    if off_time <= time_now and time_now <= on_time: # off if inside band
                        self.set_circuit(index, on=False)
                        print("off_time: "+str(off_time)+" current: "+str(time_now)+" on_time: "+str(on_time))
                    else:   # outside band turn on
                        self.set_circuit(index, on=True)
                        print("off_time: "+str(off_time)+" current: "+str(time_now)+" on_time: "+str(on_time))
                elif on_time < off_time: # on band ____---_____
                    print("on band mode")
                    if off_time <= time_now and time_now <= on_time: # on if inside band
                        self.set_circuit(index, on=True)
                        print("on_time: "+str(on_time) + " current: "+str(time_now)+" off_time: "+str(off_time))
                    else:   # outside band turn off
                        self.set_circuit(index, on=False)
                        print("on_time: "+str(on_time) + " current: "+str(time_now)+" off_time: "+str(off_time))  
                    
        time.sleep(60)
        self.schedule_handler()

def set_True(vec, index):
    vec[index]=True


    