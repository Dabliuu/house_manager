
import sys
import json
import os
import subprocess

import controllers
# from MyDbManager import MyDbManager

import time
import logging

from xbee import SDLA_grid

class Model:

    def __init__(self, controller, config):

        self.controller = controller
        self.currentConfig = config

        # initialize de databases managers objects:
        # self.myDatabaseManager = MyDbManager(self)  # the default value is True

        #  initialize the basic manager information:
        self.current_user = ""
        self.center_name = ""
        self.mySensors = []

        # initialize the xbee grid:
        self.XbeeGrid = SDLA_grid()

        #self.myDatabaseManager.configure_local_db()
        print("model init done!")


    def bar_handlers(self):
        pass

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


