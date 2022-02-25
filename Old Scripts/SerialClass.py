# create class to get data from serial connection

import serial
import time
import csv
import random


class SerialData:
    def __init__(self, num_cells):
        # initialize size variables
        self.num_cells = num_cells

        # initialize time and data values
        self.temp = time.localtime()
        self.data = [None]*num_cells

        # open serial communication
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.port = 'COM7'
        self.ser.timeout = 3  # for the read_until()'s, blocking stops after 3 seconds
        self.ser.open()

        # wait for serial to connect
        while not self.ser.is_open:
            print('not connected')
            time.sleep(1)
        time.sleep(3)
        if self.ser.in_waiting > 0:
            self.ser.reset_input_buffer()
        print('connected')

        # initialize log file
        self.filename = f"logs/log_{time.time_ns()}.csv"
        print(self.filename)
        self.fields = ["Time"]
        for i in range(num_cells):
            self.fields.append(f"Cell {i+1}")
        with open(self.filename, 'w', newline='') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(self.fields)

    def get_data(self):
        '''
        Reads data from serial comms/buffer
        outputs to class variable self.data while recording time in self.time
        reads data from esp32, outputs to class variable and csv log
        '''
        # check if there is data in the input buffer, return 0 if not ready, 1 if data is ready
        if self.ser.in_waiting == 0:
            ready = 0
            # print("not ready")
            return ready, self.temp, self.data
        else:
            ready = 1
            # print("ready")
            self.temp = time.localtime()

        # find beginning of a message packet
        self.ser.read_until(b'<\r\n')

        # read in serial values
        for i in range(self.num_cells):
            line = self.ser.readline().decode('utf-8').rstrip()
            self.data[i] = float(line)
            # print(line)
        print(time.localtime())
        print(self.data)
        # call log_data
        self.log_data([time.time_ns()] + self.data)

        # return information
        return ready, self.temp, self.data

    # logs a line of data
    def log_data(self, line):
        with open(self.filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(line)

    def send_valve_cmd(self, cell, state, ms=1000):
        # Other app sends command to open/close a specific valve
        # :param cell: cell number (index starting at 0
        # :param state: 0: both valves closed, 1: inlet open, 2: outlet open, 3: both open
        # :param time: time for valve command, default = 1000 milliseconds
        # :return: no return

        msg = f"{cell},{state},{ms}>"
        print(f"Sending: {msg}")
        self.ser.write(msg.encode('utf-8'))


if __name__ == '__main__':
    n_cells = 6
    S = SerialData(n_cells)
    while True:
        # S.get_data()
        S.send_valve_cmd(random.randint(0, 5), random.randint(0, 3), random.randint(250, 1000))

        time.sleep(0.5)
        while S.ser.in_waiting:
            print(S.ser.readline())
