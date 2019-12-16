# Instalador de files (ejecutar como administrador):
import os
import platform
import subprocess
from subprocess import check_output
import json


def main():

    id_client = "54681120821-0aai4bne8f5q0dnt969bre23564occgv.apps.googleusercontent.com"
    secret_client = "9WI7OSoOJfZEvrWxnuwJ53CQ"

    config = {
        "OS_System": platform.system(),
        "Machine": platform.machine(),
        "OS_Version": platform.platform(),
        "encodingFormat":"utf-8"
    }
    print("El sistema operativo es: " + config["OS_System"])
    print("La maquina detectada es: " + config["Machine"])
    print("La version de sistema es fue: " + config["OS_Version"])

    """----A continuacion se tiene una estructura de switch con un diccionadio y varias funciones:----"""

    def if_windows_10():  # ejecuto los datos de configuracion para windows 10
        config["encodingFormat"] = "cp437"

        comands = [
            "python  -V",  # prueba de version, se requiere la 2.7:
            "python -m pip install --upgrade pip",  # actulizar el instalador pip
            "pip install --upgrade setuptools",  # upgrading some tools needed to install the packages
            "pip install -U PySide",  # instala el modulo pyside1
            "pip install MySQL-connector-python",  # intall the mysql module for accesing database (localy and fast)

            #"pip install Pyrebase", # this is necesary for managing the database system

            "pip install pyqtgraph", # # install the module PyQtGraph for ploting using pyside or qt
            
            "pip install  -U pymodbus"
        ]

        for comand in comands:
            print("se esta ejecutando el comando:")
            print(comand)
            result = check_output(comand, shell=True)  # retorna bytes de respuesta
            print("el resultado es:")  # 'cp437' is the decoding tipe for windows
            print(result.decode(config["encodingFormat"], "replace"))

        # install the gcp (does not exist a way using shell like in linux, but this is close enough)
        comands = [
            "pip install --upgrade google-cloud",
            "pip install google-cloud-storage",
            "pip install --upgrade google-api-python-client",
            "pip install --upgrade google-api-python-client oauth2client",
            "pip install --upgrade google-auth"
        ]
        for comand in comands:
            print("se esta ejecutando el comando:")
            print(comand)
            result = check_output(comand, shell=True)  # retorna bytes de respuesta
            print("el resultado es:")  # 'cp437' is the decoding tipe for windows
            print(result.decode(config["encodingFormat"], "replace"))


        comand = {
            # this wil lead to a google session initializacion to get the credentials
            "gcloud auth application-default login"
            # the credential .json are stored on de disk and can be accesible by Application Default Credentials. request
            
            # create an environment variable (new) to the credential created:
            # 'setx GOOGLE_APPLICATION_CREDENTIALS "C:\Users\USER\Documents\PycharmProyects\housemanager_pyside1\certificates\IotHighway-66fad733b0bcIotHighway-66fad733b0bc.json"' #this should be a low permision certificate from a service account
        }

        # to launch the SDK:
        comand = "gcloud init"
        print("se esta ejecutando el comando:")
        print(comand)
        result = check_output(comand, shell=True)  # retorna bytes de respuesta
        print("el resultado es:")  # 'cp437' is the decoding tipe for windows
        print(result.decode(config["encodingFormat"], "replace"))

    def if_mac_os():  # ejecuto la rutina de configuracion para ios
        config["encodingFormat"] = "utf-8"

    def if_linux_raspi():  # ejecuto la rutina de configuracion para debian os:
        config["encodingFormat"] = "cp1252"

        comands = [
            "python  -V",  # prueba de version, se requiere la 2.7:
            "sudo pip install --upgrade pip",  # actulizar el instalador pip
            "sudo pip install --upgrade setuptools",  # upgrading some tools needed to install the packages

            "sudo apt-get install build-essential git cmake libqt4-dev libphonon-dev python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev libqtwebkit-dev" # required to install pyside
            "sudo easy_install PySide",  # instala el modulo pyside1

            "sudo pip install mysql-connector",  # intall the mysql module for accesing database (localy and fast)

            "sudo pip install pyqtgraph",  # # install the module PyQtGraph for ploting using pyside or qt

            "pip install matplotlib"  # this is for interactive plts in pyqtgraph
        ]

        for comand in comands:
            print("se esta ejecutando el comando:")
            print(comand)
            result = check_output(comand, shell=True)  # retorna bytes de respuesta
            print("el resultado es:")  # 'cp437' is the decoding tipe for windows
            print(result.decode(config["encodingFormat"], "replace"))

        # now to install the sql server
        comands = [

            # first way i tryed
            "sudo su" # start super user mode
            "curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -" # here we are adding this key as an apt-get repository
            "curl https://packages.microsoft.com/config/ubuntu/16.04/mssql-server.list > /etc/apt/sources.list.d/mssql-server.list" # this downloads a file from a url (the lists of posible downloadables)
            "sudo apt-get update" # update the downloader manager for ubuntu
            "sudo apt-get install mssql-server"
            
            #second way:
            "sudo rpi-update f6eef32dd6388c3b04dbf462bd324d93281bf397"
            "sudo apt-get update && sudo apt-get upgrade"
            "sudo apt-get install mysql-server --fix-missing"

        ]



        # now wee need to install de SDK
        comands = [
            # Create an environment variable for the correct distribution:
            'export CLOUD_SDK_REPO = "cloud-sdk-$(lsb_release -c -s)"',
            # Add the Cloud SDK distribution URI as a package source:
            'echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list',
            # Import the Google Cloud public key:
            'curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -',
            # Update and install the Cloud SDK:
            'sudo apt-get update & & sudo apt-get install google-cloud-sdk',
            # install these additional components:
            'sudo apt-get install google-cloud-sdk-app-engine-python',
            'sudo apt-get install google-cloud-sdk-app-engine-python-extras',
        ]
        for comand in comands:
            print("se esta ejecutando el comando:")
            print(comand)
            result = check_output(comand, shell=True)  # retorna bytes de respuesta
            print("el resultado es:")  # 'cp437' is the decoding tipe for windows
            print(result.decode(config["encodingFormat"], "replace"))

        comands = [
            # for creating an enviroment variable
            "export VAR=VALUE"

        ]

        # to launch the SDK:
        comand = "gcloud init"
        print("se esta ejecutando el comando:")
        print(comand)
        result = check_output(comand, shell=True)  # retorna bytes de respuesta
        print("el resultado es:")  # 'cp437' is the decoding tipe for windows
        print(result.decode(config["encodingFormat"], "replace"))

    options = {"Windows": if_windows_10,
               "macOS": if_mac_os,
               "Linux": if_linux_raspi
               }
    # ejecuto el switch
    options[config["OS_System"]]()


    """------------------------------------------fin del switch-------------------------------------------------"""


def subscribe_ip():
    # using this to get the computer public ip
    # my_ip = urlopen('http://ip.42.pl/raw').read()
    # print(my_ip)
    result = []
    # now proccess data from google iot-db description:
    result = check_output("gcloud sql instances describe iot-db", shell=True)  # retorna bytes de respuesta
    print(result)
    pos = result.find("authorizedNetworks", 50)  # counts the first as position cero
    end_pos = result.find("ipv4Enabled", pos)  # counts the first as position cero
    
    """ 
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
    """
    # print("gcloud sql instances patch iot-db --authorized-networks = " + str_ips + my_ip + "/24")
    # comand_with_response("gcloud sql instances patch iot-db --authorized-networks=" + str_ips + my_ip, "y")

def comand_with_response(comand, *responses):
    print("executing comand:", comand)
    p = subprocess.Popen(comand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    newline = os.linesep  # this is the object that handles the comunication
    print("responses handled: ",responses)
    p.communicate(newline.join(responses))
    print("done")

if __name__ == "__main__":
    main()
