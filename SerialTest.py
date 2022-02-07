#tests raw data coming in from esp

import serial
import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM7'
ser.open()

while not ser.is_open:
    print('not connected')
    time.sleep(1)


while True:
    #localtime = time.localtime()
    line = ser.readline()
    print(line)