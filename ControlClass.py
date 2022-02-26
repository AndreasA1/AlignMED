import time
import csv
import numpy as np
import board
import busio

# components imports
from adafruit_mcp230xx.mcp23017 import MCP23017 #I/O expander library
import adafruit_tca9548a # i2c expander library
import adafruit_mprls # pressure sensor library

import sys
import zmq

from time import sleep


class Controller:
    def __init__(self, n_cells):
        print("initializing controller class")

        # initialize class-level values
        self.n_cells = n_cells
        self.cell_states = np.zeros(shape=(2*n_cells,))
        self.cell_state_duration = np.zeros(shape=(2*n_cells,))

        '''
        # zmq setup
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:6000")
        cmd_filter = "cmd"
        self.socket.setsockopt_string(zmq.SUBSCRIBE, cmd_filter)
        '''

        # open file for data logging
        self.filename = f"logs/log_debug.csv"
        '''
        # self.filename = f"logs/log_{time.time_ns()}.csv"
        # print(self.filename)
        self.fields = ["Time"]
        for i in range(num_cells):
            self.fields.append(f"Cell {i+1}")
        with open(self.filename, 'w', newline='') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(self.fields)
        '''

        # i2c bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # mcp and tca scaffolding
        n_mcp = 8
        n_mcp_gpio = 16
        self.mcp = [None for i in range(n_mcp)]
        self.mcp_pins = [[None for i in range(n_mcp_gpio)] for j in range(n_mcp)]
        n_tca = 4
        n_tca_i2c = 8
        self.tca = [None for i in range(n_tca)]
        self.tca_i2c = [[None for i in range(n_tca_i2c)] for j in range(n_tca)]

        # init reset msp
        self.setup_mcp(7)

        # setup the rest of the main i2c devices
        # self.setup_i2c()

    # gets pressure sensor values, formats into a row, and appends to log file
    def get_sensor_values(self):
        line = [time.time_ns()]
        for i in range(self.n_cells):
            value = 1.0  # call pressure_val(i)
            line.append(value)
            self.log_data(line)

    # gets the value for one pressure sensor
    def pressure_val(self, sensor_id):
        try:
            return 1.0
        except:
            return 1.0

    # logs a line of data to the log file
    def log_data(self, line):
        with open(self.filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(line)

    def setup_i2c(self):
        # whole function needs a rework
        # 1- connect to all mcp's, drive outputs low
        # 2- connect to all tca's
        # 3- setup i2c lines on tca's


        # setup mcp7
        self.mcp0 = MCP23017(self.i2c, address=0x27)
        self.mcp0_p0 = mcp0.get_pin(0)
        self.mcp0_p0.switch_to_output(value=True)

        # drive reset pins high
        self.mcp0_p0.value = True

        # setup tca objects
        self.tca1 = adafruit_tca9548a.TCA9548A(self.i2c, address=0x70)

        # tie pressure sensors to tca i2c lines
        self.mpr1 = adafruit_mprls.MPRLS(self.tca1[1], psi_min=0, psi_max=25)
        return

    def setup_mcp(self, mcp_id, n_pins=16):
        mcp_init = MCP23017(self.i2c, address=0x20+mcp_id)
        self.mcp[mcp_id] = mcp_init
        self.mcp_pins[mcp_id][0] = self.mcp[mcp_id].get_pin(0)
        self.mcp_pins[mcp_id][0].switch_to_output(value=True)
        self.mcp_pins[mcp_id][0].value = True

        # if mcp_id == 7, drive all pins high

    def setup_tca(self, tca_id, n_sensors=8):
        self.tca[tca_id] = adafruit_tca9548a.TCA9548A(self.i2c, address=hex(70+tca_id))

    def setup_mpr(self, sensor_id):
        tca_id = sensor_id // 8
        line_id = sensor_id % 4
        # really not confident this will work
        self.tca_i2c[tca_id][line_id] = adafruit_mprls.MPRLS(self.tca[tca_id][line_id], psi_min=0, psi_max=25)

    def receive_cmd(self):
        try:
            cmd = self.socket.recv(flags=zmq.NOBLOCK)
            c = cmd.split()  # put fields here that we want
            print(cmd)
            return cmd
        except zmq.Again as e:
            print("no cmd received")
            return 0


if __name__ == '__main__':
    print("we controlling")
    num_cells = 4
    con = Controller(num_cells)

    while True:
        sleep(1)


    # while True:
    # cycle through stuff here
