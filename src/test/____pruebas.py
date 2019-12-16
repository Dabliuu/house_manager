# -*- coding: utf-8 -*-
import sched
import urllib
import os
from functools import partial
from threading import Timer
import threading
import time
import subprocess

import models

import google as google
from google.cloud import storage
from google.protobuf import service

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from urllib2 import urlopen
from subprocess import check_output


if __name__ == "__main__":

    """
    # downoading the file from google
    url = 'https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe'

    def tick(text):
        print(text+".")
        time.sleep(1)  # slep for 1 second
        print(text+"..")
        time.sleep(1)  # the oposite of slleep is join()
        print(text+"...")
        time.sleep(1)


    # t = Timer(3, tick)# after 3 seconds the tick will execute 1 time
    # t = threading.Thread(target=tick) # this one executes the parallel thread immediately

    # con un decorator nos ahorramos un poco de codigo
    t = RepeatedTimer(3, tick, "downloading")
    urllib.urlretrieve(url, "./cloud_sql_proxy.exe")
    t.stop()
    print("¡download finished!")

    # execute file
    print("executing file")
    t = RepeatedTimer(3, tick, "opening")
    os.system('"cloud_sql_proxy.exe"')#  *, stdin=None, stdout=None, stderr=None, shell=False
    t.stop()
    print("file executed")

    """

    # with this function we veryfy the autentication token given by gcp and can acces son data
    def implicit():
        from google.cloud import storage

        # If you don't specify credentials when constructing the client, the
        # client library will look for credentials in the environment.
        storage_client = storage.Client()

        # Make an authenticated API request
        buckets = list(storage_client.list_buckets())
        print(buckets)

    def explicit():

        # Explicitly use service account credentials by specifying the private key
        # file.
        print('C:\Users\USER\AppData\Roaming\gcloud\\application_default_credentials.json')
        storage_client = storage.Client.from_service_account_json(
            'C:\Users\USER\AppData\Roaming\gcloud\\application_default_credentials.json'
        )
        # Make an authenticated API request
        buckets = list(storage_client.list_buckets())
        print(buckets)

    def explicit_compute_engine(project):
        from google.auth import compute_engine
        from google.cloud import storage

        # Explicitly use Compute Engine credentials. These credentials are
        # available on Compute Engine, App Engine Flexible, and Container Engine.
        credentials = compute_engine.Credentials()

        # Create the client using the credentials and specifying a project ID.
        storage_client = storage.Client(credentials=credentials, project=project)

        print(storage_client)

        # Make an authenticated API request

    def e_mail_auth():



        # If modifying these scopes, delete the file token.json.
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('./../certificates/IotHighway-66fad733b0bc.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        # Call the Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])

    # obtener el email del usuario:
    def new_obtain_email():

        people_resource = service.people()
        people_document = people_resource.get(userId='me').execute()

        print("ID: " + people_document['id'])
        print("Display name: " + people_document['displayName'])
        print("Image URL: " + people_document['image']['url'])
        print("Profile URL: " + people_document['url'])

    """
    # proccesing data:
    result = check_output("gcloud sql instances describe iot-db", shell=True)  # retorna bytes de respuesta
    print(result)
    pos = result.find("authorizedNetworks", 50)  # counts the first as position cero
    end_pos = result.find("authorizedNetworks", pos)  # counts the first as position cero
    lines = [line.rstrip('\n') for line in result]
    ip_info = lines[pos:end_pos]
    print(ip_info)
    """

    def comand_with_response(comand, *responses):
        print("executing comand:", comand)
        p = subprocess.Popen(comand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        newline = os.linesep  # this is the object that handles the comunication
        print("responses handled: ",responses)
        p.communicate(newline.join(responses))
        print("done")

    #comand_with_response("gcloud sql instances patch iot-db --authorized-networks = 186.27.130.100", "y")

    def printing():
        print("hola")

def subscribe_ip():
    # using this to get the computer public ip
    my_ip = urlopen('http://ip.42.pl/raw').read()
    print(my_ip)

    # now proccess data from google iot-db description:
    result = check_output("gcloud sql instances describe iot-db", shell=True)  # retorna bytes de respuesta
    print(result)
    pos = result.find("authorizedNetworks", 50)  # counts the first as position cero
    end_pos = result.find("ipv4Enabled", pos)  # counts the first as position cero
    char_ip_info = str(result[pos:end_pos])
    print(char_ip_info)

    more_ips = True
    server_ips = []
    while more_ips:
        # find the fist position valu object:
        ip_init_pos = char_ip_info.find("value:") + "value:".__len__()

        if ip_init_pos == "value:".__len__() - 1:
            more_ips = False
            break
        else:
            ip_final_pos = char_ip_info.find("\n", ip_init_pos)
            server_ips.append(char_ip_info[ip_init_pos:ip_final_pos].strip())
            # delimit the string:
            char_ip_info = char_ip_info[ip_final_pos:]
        print(char_ip_info)

    print(server_ips)

    str_ips = ""
    for ip in server_ips:
        str_ips += ip + ","

    print("gcloud sql instances patch iot-db --authorized-networks = " + str_ips + my_ip + "/24")
    comand_with_response("gcloud sql instances patch iot-db --authorized-networks=" + str_ips + my_ip,
                               "y")


#subscribe_ip()

def decor(func):
    def wraper(name, *args, **kargs):
        print("."+name+".")
        print("decorated")
        func(name, *args, **kargs)
    return wraper

@decor
def my_func(name, num):
    print("my name is: "+name+", with num: "+str(num))

# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from numpy import arange, sin, cos, pi
import pyqtgraph as pg
import sys

"""
class Plot2D():
    def __init__(self):
        self.traces = dict()

        #QtGui.QApplication.setGraphicsSystem('raster')
        self.app = QtGui.QApplication([])
        #mw = QtGui.QMainWindow()
        #mw.resize(800,800)

        self.win = pg.GraphicsWindow(title="Basic plotting examples")
        self.win.resize(1000,600)
        self.win.setWindowTitle('pyqtgraph example: Plotting')

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        self.canvas = self.win.addPlot(title="Pytelemetry")

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def trace(self,name,dataset_x,dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x,dataset_y)
        else:
            self.traces[name] = self.canvas.plot(pen='y')

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    p = Plot2D()
    i = 0

    def update():
        global p, i
        t = np.arange(0,3.0,0.01)
        s = sin(2 * pi * t + i)
        c = cos(2 * pi * t + i)
        p.trace("sin",t,s)
        p.trace("cos",t,c)
        i += 0.1

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)

    p.start()
"""

"""-------------------- bifasic counter measurement
import pymodbus
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from pymodbus.transaction import ModbusRtuFramer

client = ModbusClient(method = "rtu", port="/dev/ttyUSB0",stopbits = 1, bytesize = 8, parity = 'E', baudrate= 9600)

#Connect to the serial modbus server
try:
    connection = client.connect()
    print connection
    result = client.read_holding_registers(0x00, 2, unit=0xff)
    print(result)
except Exception as e:
    print e



#Closes the underlying socket connection
client.close()

---------------------------------------------------"""