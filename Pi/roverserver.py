#!/usr/bin/env python

# example command set: true,stop,75
import socket
import sys
import traceback
import time
import syslog
import time
import serial
import subprocess
#import psutil


#expects strings of the form:
#C:80:75:1:1:E

#C indicates start of command
#first 2 digits are motor speeds, positive or negative to indicate direction
#third int is throttle percentage
#fourth is binary - should I return sensor values, 0 or 1
#fifth is binary - 1 = lights on, 0 = lights off
#ends with E, easier than detecting newline

def getSignalStrength():
    # signal strength
    cmd = subprocess.Popen('iwconfig wlan0', shell=True,
                           stdout=subprocess.PIPE)


    strength = str(cmd.communicate()[0])
    strength = strength.split(" Signal level=")
    strength = strength[1].split(" dBm")
    return strength[0]


#these could easily be combined and save a system call, if we want to use both

def getLinkQual():
    # Link Qual
    cmd = subprocess.Popen('iwconfig wlan0', shell=True,
                           stdout=subprocess.PIPE)

    strength = str(cmd.communicate()[0])
    strength = strength.split(" Link Quality=")
    strength = strength[1].split(" Signal level=")
    return strength[0]


value = 0

syslog.syslog('Rover: Server starting....')

host = ''
port = 6000
backlog = 1
size = 4096
count = 0

ser = serial.Serial(port='/dev/ttyS0', baudrate=57600, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

while 1:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((host, port))
    s.listen(0)

    print("Rover: Waiting for connection...")

    client, address = s.accept()
    s.settimeout(1.0)
    client.settimeout(1.0)

    print("Rover: Got client connection from " + str(address[0]))

    while (1):
        try:
            clientReq = client.recv(size)
        except:
            print("Rover: Socket error")
            break

        if (clientReq == ""):
            print("Rover: Connection broken.")
            break

        ser.write(clientReq)

        temp = str(clientReq)

        values = temp.split(":")
        if (len(values) > 2):
            if (values[3] == "1"):
                returnSensors = True
            else:
                returnSensors = False

        response = ser.readline()
        response = response.decode('utf-8')

        if (returnSensors):
            
            signal_strength = getSignalStrength()
            linkQuality = getLinkQual()
            response = response.rstrip() + str(signal_strength) + ":" + str(linkQuality) + ":"

        client.sendall(response.encode('utf-8'))

    print("Rover: Shutting down server socket.")
    s.shutdown(1)
    s.close()


