


from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress, XBeeDevice


import serial.tools.list_ports
import struct
import numpy as np

from functools import partial

import copy
import signal

import time

import concurrent.futures

# dafo tienes que trabajar mas para que no te vaya mal en la tesis

# indentify the comport that has the usb to rs485 converter:
def get_com_port():
    
    # The id of the hardware (zigbee module) is:
    USBTORS485_VID = 1027
    USBTORS485_PID = 24577

    # get the list of the comports availables
    com_port = None
    comlist = serial.tools.list_ports.comports()
    print("The COM list ports are: " + str(list(comlist))) # com list is a list of objects containing all the info of the ports connected

    # search in the list of connected hardware the id's specified
    for element in comlist:
        
        print("the hardware {} vid is: {}".format(str(element), element.vid))
        print("the hardware {} pid is: {}".format(str(element), element.pid))

        if element.vid == USBTORS485_VID and element.pid == USBTORS485_PID:
            com_port = element.device

    # check if we found the hardware connected
    if com_port == None:  
        print("The USB to RS485 hardware is not connected")
    else:
        print("Hardware connected to COM port: " + com_port)

    return com_port


class Xbee_sensor_manager():
    def __init__(self, connected_port:str):
        
        # initialize important variables 
        self.local_device = None
        self.PORT = connected_port

        # set up the variables
        self.BAUD_RATE = 57600

    def get_remote_device_address(self, xbee_remote_node_id:str = "WFM"):

        try:
            if self.local_device == None:
                self.local_device = XBeeDevice(self.PORT, self.BAUD_RATE)
                self.local_device.open()      
                self.local_device.flush_queues()  

            # initialize the network using the local node
            xbee_network = self.local_device.get_network()

            # Configure the discovery timeout, in SECONDS.
            xbee_network.set_discovery_timeout(4)

            print("the xbee network is: "+ str(xbee_network))
            
            # Get the remote device configuration:
            t_reference = time.time() # time in seconds
            while True:
                remote_device = xbee_network.discover_device(xbee_remote_node_id)
                if remote_device != None:
                    print("---->> adquired!")
                    break
                elif time.time() > t_reference + 10: #segundos
                    print("---->> timeout")
                    assert "timeout configureins sensor"
                    break
                else:
                    print("---->> no response yet")
                time.sleep(1)

            address = remote_device.get_64bit_addr()

            print("the address of "+xbee_remote_node_id+" is: "+ str(address))

            return str(address)

        except Exception as e:
            print("exception getting the address of the device "+xbee_remote_node_id+". Error: "+ e)

        finally:
            if self.local_device is not None and self.local_device.is_open():
                self.local_device.close()
                self.local_device = None
        

    def config_xbee_sensor(self, xbee_remote_address:str = "0013A200410704E8") -> type(RemoteXBeeDevice):

        if self.local_device == None:
            self.local_device = XBeeDevice(self.PORT, self.BAUD_RATE)
            self.local_device.open()      
            self.local_device.flush_queues()  

        remote_device = RemoteXBeeDevice(self.local_device, XBee64BitAddress.from_hex_string(xbee_remote_address))

        print("The remote device id is: "+str(remote_device))
        #assert remote_device is not None, "Could not find the remote device"
        

        t_reference = time.time() # time in seconds
        while True:
            remote_device = RemoteXBeeDevice(self.local_device, XBee64BitAddress.from_hex_string(xbee_remote_address))
            if remote_device != None:
                print("---->> adquired!")
                break
            elif time.time() > t_reference + 20: #segundos
                print("---->> timeout")
                assert "timeout configureins sensor"
                break
            else:
                print("---->> no response yet")
            time.sleep(1)


        return remote_device

    
    def get_xbee_data(
        self,
        remote_device: type(RemoteXBeeDevice),  
        xbee_data_type_id: bytearray = bytearray([48, 48])
        ) -> float:
        
        
        TIMEOUT_TIME_MS = 500 # the amount to timeout

        print(">>Remote device: "+str(remote_device))
        print(">>data_type id: "+str(xbee_data_type_id))

    
        #def my_data_received_callback(xbee_message):
        #
        #    response_bytes = xbee_message.data
        #    print(">>>> byte data without decode: "+str(response_bytes))
        #    data = xbee_message.data.decode("utf-8")
        #    print(">>>> Received data: " +  data)
            

        # send and receive the data         
        self.local_device.send_data(remote_device, xbee_data_type_id)
        print("--> DATA SENDED")

        # Add the callbac
        # k.
        #self.local_device.add_data_received_callback(my_data_received_callback)
    

        t_reference = time.time() # time in seconds
        while True:
            xbee_message = self.local_device.read_data()
            if xbee_message != None:
                print("---->> adquired!")
                break
            elif time.time() > t_reference + TIMEOUT_TIME_MS/1000: #segundos
                print("---->> timeout")
                break
            else:
                print("---->> no response yet")
            time.sleep(0.1)

        try:
            

            # Format the data
            print(xbee_message.data)
            response_bytes = copy.deepcopy(xbee_message.data)
            reversed_bytes = list()

            """
            for i in reversed(response_bytes):
                reversed_bytes.append(i)
            
            print("-->> the response bytes are: "+str(response_bytes))
            """

            #print("-->> the decoded  bytes are: "+response_bytes.decode("cp437"))
        
            separated = list()

            separated.append(response_bytes[0:4])
            separated.append(response_bytes[4:8])
            separated.append(response_bytes[8:12])
            separated.append(response_bytes[12:16])
            separated.append(response_bytes[16:20])

            print("-->> the separated bytes are: "+str(separated))

            #int_value = int.from_bytes(separated[0], byteorder='big', signed=False)
            #print("-->> the int value is: "+str(int_value))


            float_vrms = struct.unpack('>f', separated[0])
            print("Vrms: "+str(float_vrms))

            float_irms = struct.unpack('>f', separated[1]) 
            print("Irms: "+str(float_irms))

            float_pinst = struct.unpack('>f', separated[2])
            print("instant p: "+str(float_pinst))

            float_e = struct.unpack('>f', separated[3])
            print("Energy: "+str(float_e))

            float_fp = struct.unpack('>f', separated[4])
            print("Power factor: "+str(float_fp))
            
            #self.local_device.flush_queues()

            """
            # separate the array in th 5 diferent structs Vrms, Irms, P_instant, PH, FP
            np.array(response_bytes)
            byte_data_Vec = np.split(response_bytes, 5)
            print("the byte data vec"+str(byte_data_Vec))

            
            print("byte data without decode: {}".format(response_bytes))
            float_value = struct.unpack('f', response_bytes) 
            print("data decoded to 4 bytes float: {}".format(float_value))
            print("From %s >> decoded message: %s" % (
                xbee_message.remote_device.get_64bit_addr(),
                                    float_value)
                )
            return float_value
            """


            return (float_vrms, float_irms, float_pinst, float_e, float_fp)
        
        except Exception as e:
            print("Error getting the data: "+str(e))
            return None

    def send_xbee_data(
        self, 
        remote_device: type(RemoteXBeeDevice),  
        xbee_data_type_id: bytearray = bytearray([1,1])):
        # send and receive the data         
        self.local_device.send_data(remote_device, xbee_data_type_id)
        print("--> DATA SENDED")


    def close_manager(self):
        if self.local_device is not None and self.local_device.is_open():
            self.local_device.close()
            self.local_device = None


class SDLA_grid():

    def __init__(self):
        
        port = get_com_port()
        self.my_manager = Xbee_sensor_manager(port)

        # -----------xbees list of electric devices----------------

        self.EM_adresses=[
            self.my_manager.get_remote_device_address("EM_1"),
            self.my_manager.get_remote_device_address("EM_2")
        ]
        
        print("--->>> THE XBEES EM ADRESS ARE: "+str(self.EM_adresses))

        #create the xbee remote objects for the electric using the address:
        self.EM_xbees = list()

        for adress in self.EM_adresses:
            self.EM_xbees.append(self.my_manager.config_xbee_sensor(adress))

        print("--->>> THE XBEES EM ARE: "+str(self.EM_xbees))

        # -------------xbees list of relay grids devices--------------

        self.ACT_adresses = [
            self.my_manager.get_remote_device_address("ACT_1"),
            self.my_manager.get_remote_device_address("ACT_2"),
            self.my_manager.get_remote_device_address("ACT_3"),
            self.my_manager.get_remote_device_address("ACT_4")
        ]

        print("--->>> THE XBEES ACT ADRESS ARE: "+str(self.ACT_adresses))

        #create the xbee remote objects for the electric using the address:
        self.ACT_xbees = list()

        for adress in self.ACT_adresses:
            self.ACT_xbees.append(self.my_manager.config_xbee_sensor(adress))
        
        print("--->>> THE XBEES ACT ARE: "+str(self.ACT_xbees))

        """
        # this is a delayed thread to handle the remote mode:
        self._timer = threading.Timer(
            interval= self.currentConfig["report_rate"],
            function = self.report_handler
        )
        # self._timer.setDaemon(True)
        self._timer.start()
        """           

                
        
            
    def get_energy(self, serial_number:int = 1):
        try:
            (float_vrms, float_irms, float_pinst, float_e, float_fp) = self.my_manager.get_xbee_data(
                self.EM_xbees[serial_number-1], 
                "EM"
            )
            return float_e
        except Exception as e:
            print("Error getting the data from the function (xbee file): "+str(e))
            return None
        

    def get_irms(self, serial_number:int = 1):
        (float_vrms, float_irms, float_pinst, float_e, float_fp) = self.my_manager.get_xbee_data(
            self.EM_xbees[serial_number-1], 
            "EM"
        )
        return float_irms

    def get_fp(self, serial_number:int = 1):
        (float_vrms, float_irms, float_pinst, float_e, float_fp) = self.my_manager.get_xbee_data(
            self.EM_xbees[serial_number-1], 
            "EM"
        )
        return float_fp

    def set_circuit(self, toOn = False,  serial_number:int = 1, circuit_number = 1):
        
        index = self.ACT_xbees[serial_number]
        print("--->>>> serial_number: "+str(serial_number))
        print("--->>>> circuit_number: "+str(circuit_number))
        print("printed: "+str(index))
        if toOn:
            self.my_manager.send_xbee_data(
                index,
                bytearray([circuit_number, 1])
            )
        else:
            self.my_manager.send_xbee_data(
                index,
                bytearray([circuit_number, 0])
            )

    def end(self):
        self.my_manager.close_manager()


