# Copyright 2017, Digi International Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from digi.xbee.devices import XBeeDevice

import serial.tools.list_ports

import struct


# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 57600
WATTER__REMOTE_NODE_ID = "WFM" # watter flow measurement sensor
FLOW__REQUEST_PDU = bytearray([48, 48]) # request pdu for instant water flow

RELAY__REMOTE_NODE_ID = "ACTUATOR" # watter flow measurement sensor
CIRCUIT__COMAND_PDU = bytearray([4, 1]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)

POWER__REMOTE_NODE_ID = "EM_1" # watter flow measurement sensor
#POWER_ADDRESS =
POWER__COMAND_PDU = bytearray([69, 77]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)


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




# TODO: Replace with the serial port where your local module is connected to. 
PORT = get_com_port()



def main():

    xbee_sensor_id = POWER__REMOTE_NODE_ID
    xbee_data_type_id = POWER__COMAND_PDU

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

        def data_receive_callback(xbee_message):
            response_bytes = xbee_message.data
            print("byte data without decode: {}".format(response_bytes))
            #float_value = struct.unpack('f', response_bytes) 
            #print("data decoded to 4 bytes float: {}".format(float_value))

            #print("From %s >> decoded message: %s" % (xbee_message.remote_device.get_64bit_addr(), float_value))

        local_device.send_data(remote_device, xbee_data_type_id)
        print(">DATA SENDED")

        local_device.add_data_received_callback(data_receive_callback)
    

        print("Waiting for data...\n")
        input()

    finally:
        if local_device is not None and local_device.is_open():
            local_device.close()


if __name__ == '__main__':
    main()