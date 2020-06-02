#!/usr/bin/env python
          
      
import time
import serial

#program for sending test strings to the Arduino for rover hardware testing without a network client

#expects strings of the form:
#C:80:75:1:1:E

#C indicates start of command
#first 2 digits are motor speeds, positive or negative to indicate direction
#third int is throttle percentage
#fourth is binary - should I return sensor values, 0 or 1
#fifth is binary - 1 = lights on, 0 = lights off
#ends with E, easier than detecting newline
          
      
ser = serial.Serial(port='/dev/ttyS0',baudrate = 57600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

count = 0

while (count < 30):          
	ser.write("C:0:0:0:0:E")
	x=ser.readline()
	#print x
	count = count + 1


count = 0

while (count < 300):          
	ser.write("C:0:0:0:1:E")
	x=ser.readline()
	#print x
	count = count + 1


count = 0

while (count < 30):          
	ser.write("C:0:0:0:0:E")
	x=ser.readline()
	#print x
	count = count + 1


count = 0

while (count < 30):          
	ser.write("C:0:0:0:1:E")
	x=ser.readline()
	#print x
	count = count + 1


count = 0

while (count < 30):          
	ser.write("C:0:0:0:0:E")
	x=ser.readline()
	#print x
	count = count + 1

