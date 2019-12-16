#   _______________________________________________________________________________________
#  || - - - - - - - - - - - ||            |                                               ||
#  || - - ||||||||||||\ - - ||   AUTHOR:  |  Juan David Ramirez                           ||
#  || - - - ||| |||- ||| - -||____________|_______________________________________________||
#  || - - - ||| |||- ||| - -||            |                                               ||
#  || - - - ||| ||||||/ - - ||     DATE:  |  Junio de 2019                                ||
#  || - - - ||| - - - - - - ||____________|_______________________________________________||
#  || - - - ||| ||||||\ - - ||            |                                               ||
#  || - - - ||| |||- ||| - -||   E-MAIL:  |  juan.ramirez.villegas@correounivalle.edu.co  ||
#  || - - - ||| ||||||/ - - ||____________|_______________________________________________||
#  || - - -|||| |||- ||\ - -||                                                            ||
#  || -|||||| - - - - - - - ||               * * * * USE WISELY * * * *                   ||                                   
#  || - - - - - - - - - - - ||____________________________________________________________||                                                             
#  ****************************************************************************************


from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress, XBeeDevice


import serial.tools.list_ports
import struct
import numpy as np

from functools import partial

import copy
import signal

import time
import timeout_decorator


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

    def get_remote_device_address(self, xbee_remote_node_id:str = "ACT_1"):

        try:
            if self.local_device == None:
                self.local_device = XBeeDevice(self.PORT, self.BAUD_RATE)
                self.local_device.open()      
                self.local_device.flush_queues()  

            # initialize the network using the local node
            xbee_network = self.local_device.get_network()

            # Configure the discovery timeout, in SECONDS.
            xbee_network.set_discovery_timeout(4.1) 

            print("the xbee network is: "+ str(xbee_network))
            
            # Get the remote device configuration:
            remote_device = xbee_network.discover_device(xbee_remote_node_id)
            
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
        assert remote_device is not None, "Could not find the remote device"
            
        
        return remote_device

    
    def command_xbee(
        self,
        remote_device: type(RemoteXBeeDevice),  
        xbee_data_type_id: bytearray = bytearray([1,1])
        ) -> float:
        
        print(">>Remote device: "+str(remote_device))
        print(">>data_type id: "+str(xbee_data_type_id))


        # send and receive the data         
        self.local_device.send_data(remote_device, xbee_data_type_id)
        print("--> DATA SENDED")

        

        return True


    def close_manager(self):
        if self.local_device is not None and self.local_device.is_open():
            self.local_device.close()
            self.local_device = None

if __name__ == "__main__":

    import time
    import statistics
    

    try:
        
        config_vec = list()
        get_vec = list()
        NUMBER_OF_ROUNDS = 1000

        REMOTE_NODE_ID = "ACT_1"# watter flow measurement sensor
        RELAY1__COMMAND = bytearray([1,1]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)
        RELAY2__COMMAND = bytearray([2,1])
        RELAY3__COMMAND = bytearray([3,1])
        RELAY4__COMMAND = bytearray([4,1])


        __sec_1_config = time.time() # check time to benchmark

        # initialize the com port and the variables:
        com_port = get_com_port()
        xbee_manager = Xbee_sensor_manager(com_port)

        

        address = xbee_manager.get_remote_device_address(REMOTE_NODE_ID)

        print("-------->>>"+str(address))

        __sec_2_config = time.time() # check time to benchmark

        print("Time to set up the variables: " + str(__sec_2_config - __sec_1_config)+" seconds")

        for index in range(NUMBER_OF_ROUNDS):

            try:
                __sec_pre_config = time.time() # check time to benchmark

                
                remote_xbee_sensor = xbee_manager.config_xbee_sensor(address) # configure the sensor (watter sensor default)

                # print("-------->>>"+str(xbee_manager.local_device))

                __sec_pre_get = time.time() # check time to benchmark

                
                isOk_1 = xbee_manager.command_xbee(remote_xbee_sensor, RELAY1__COMMAND) # get the data (m3 value default)
                isOk_2 = xbee_manager.command_xbee(remote_xbee_sensor, RELAY2__COMMAND) # get the data (m3 value default)
                isOk_3 = xbee_manager.command_xbee(remote_xbee_sensor, RELAY3__COMMAND) # get the data (m3 value default)
                isOk_4 = xbee_manager.command_xbee(remote_xbee_sensor, RELAY4__COMMAND) # get the data (m3 value default)


                __sec_pos_get = time.time() # check time to benchmark
                
                # print("-------->>>"+str(xbee_manager.local_device))

                print("Time to make the config: " + str(__sec_pre_get - __sec_pre_config)+" seconds")
                print("Time get the info: " + str(__sec_pos_get - __sec_pre_get)+" seconds")
                print("Time to make the hole process: " + str(__sec_pos_get - __sec_pre_config)+" seconds")
                print("Lap number: "+str(index+1))

                config_vec.append(__sec_pre_get - __sec_pre_config)
                get_vec.append(__sec_pos_get - __sec_pre_get)

            except Exception as e:
                print("¡Adquisition failed, data corrupted! the error is: "+str(e))
                fail_counter += 1

            finally:
                xbee_manager.close_manager() # close the port


            # print("-------->>>"+str(xbee_manager.local_device))

        average_config_time = statistics.mean(config_vec)
        averange_get_time = statistics.mean(get_vec)
        add = average_config_time + averange_get_time
        standar_derivation = np.std( np.array(config_vec) + np.array(get_vec) )
        success_rate = (NUMBER_OF_ROUNDS - fail_counter) / NUMBER_OF_ROUNDS

        print("-------------->>> The averange config time was: "+str(average_config_time))
        print("-------------->>> The averange get time was: "+str(averange_get_time))
        print("-------------->>> The total averange time was: "+str(add))
        print("-------------->>> The standard derivation time was: "+str(standar_derivation)) # 68% of the time the adquisition process is included in one standard derivation (SD) and 95% is included in two SD
        print("-------------->>> The succes rate was: "+str(success_rate))


    except Exception as e:
        print(e)
    
    input()



    
"""
From last test 1000 POWER METTER, watter measure M3:
-------------->>> The averange config time was: 0.06054400086812547
-------------->>> The averange get time was: 0.06636708094082337
-------------->>> The total averange time was: 0.12691108180894883
-------------->>> The standard derivation time was: 0.04412038596887699
-------------->>> The succes rate was: 0.582
"""