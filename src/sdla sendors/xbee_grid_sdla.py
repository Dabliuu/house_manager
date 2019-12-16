
from digi.xbee.devices import XBeeDevice

import serial.tools.list_ports

import struct



class Watter_sensor():
    id = "WFM"# watter flow measurement sensor
    FLOW__HEADER = bytearray([48, 48]) # request pdu for instant water flow
    TEMP_HUMID__HEADER = bytearray("FE", "utf-8") # request pdu for instant temperature and humidity
    TEMP__HEADER = byt|earray("F", "utf-8") # request pdu for instant temperature
    HUMID__HEADER = bytearray("E", "utf-8") # request pdu for instant temperature

class relay_actuator():
    id = "ACTUATOR"# watter flow measurement sensor
    RELAY1__COMMAND = bytearray([1,1]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)
    RELAY2__COMMAND = bytearray([2,1])
    RELAY3__COMMAND = bytearray([3,1])
    RELAY4__COMMAND = bytearray([4,1])

class electric_actuator():
    id = "EM"# Energy metter
    INSTANT_AC_VOLTAGE__HEADER = bytearray("V", "utf-8") # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)
    INSTANT_AC_CURRENT__HEADER = bytearray("I", "utf-8")
    INSTANT_AC_POWER__HEADER = bytearray("P", "utf-8")

# indentify the comport that has the usb to rs485 converter:
def get_com_port() -> str:
    
    # The id of the hardware (usb to rs485) is:
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



def main():

    # TODO: Replace with the serial port where your local module is connected to. 
    PORT = get_com_port()
    # TODO: Replace with the baud rate of your local module.
    BAUD_RATE = 9600

    xbee_sensor_id = Watter_sensor.id
    xbee_data_type_id = Watter_sensor.FLOW__HEADER

    print(" +-----------------------------------------+")
    print(" | XBee Python Library Receive Data Sample |")
    print(" +-----------------------------------------+\n")

    local_device = XBeeDevice(PORT, BAUD_RATE)

    try:
        local_device.open()

        # initialize the network using the local node
        xbee_network = local_device.get_network()

        # Get the remote device configuration:
        remote_device = xbee_network.discover_device(xbee_sensor_id)

        print("The remote device id is: "+str(remote_device))
        if remote_device is None:
            print("Could not find the remote device")
            exit(1)


        #
        #
        #
        #
        #
        # Instantiate a remote XBee device object.
        #remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040XXXXXX"))


        def data_receive_callback(xbee_message):
            response_bytes = xbee_message.data
            print("byte data without decode: {}".format(response_bytes))
            float_value = struct.unpack('f', response_bytes) 
            print("data decoded to 4 bytes float: {}".format(float_value))

            print("From %s >> decoded message: %s" % (xbee_message.remote_device.get_64bit_addr(),
                                     response_bytes.decode('utf-8')))

        local_device.send_data(remote_device, xbee_data_type_id)
        res = local_device.read_data()
        print("res: "+res.data)

        # local_device.add_data_received_callback(data_receive_callback)
                
        print("Waiting for data...\n")

    finally:
        if local_device is not None and local_device.is_open():
            local_device.close()


if __name__ == '__main__':
    main()