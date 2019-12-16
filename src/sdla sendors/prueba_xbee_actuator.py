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

RELAY__REMOTE_NODE_ID = "ACT_3" # watter flow measurement sensor

RELAY1__COMMAND = bytearray([1,1]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)
RELAY2__COMMAND = bytearray([2,1])
RELAY3__COMMAND = bytearray([3,1])
RELAY4__COMMAND = bytearray([4,1])

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

    xbee_sensor_id = RELAY__REMOTE_NODE_ID
    xbee_data_type_id = bytearray([1,1]) # request pdu for instant water flow [CIRCUITO, STATE] (STATE = 1 | 0)

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

        local_device.send_data(remote_device, xbee_data_type_id)
        print(">DATA SENDED")
    

        print("Waiting for data...\n")
        input()

    finally:
        if local_device is not None and local_device.is_open():
            local_device.close()


if __name__ == '__main__':
    main()