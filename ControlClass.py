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
        '''

        # i2c bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # set up MCPs
        n_mcp = 8
        n_mcp_gpio = 16
        self.mcp = [None for i in range(n_mcp)]
        self.mcp_pins = [[None for i in range(n_mcp_gpio)] for j in range(n_mcp)]

        # set up TCAs
        n_tca = 4
        n_tca_i2c = 8
        self.tca = [None for i in range(n_tca)]
        self.sensor_array = [[None for i in range(n_tca_i2c)] for j in range(n_tca)]

        # init reset msp
        self.setup_mcp(7)

        # init other MCPs
        for i in range(6):
            self.setup_mcp(i)

        # init TCAs
        for i in range(n_tca):
            self.setup_tca(i)

        # init pressure sensors
        for i in range(n_cells):
            print(f"mpr: {i}")
            self.setup_mpr(i)
        # # set up the rest of the main i2c devices
        # # self.setup_i2c()

        print("success")

    def init_log_file(self):
        fields = ["Time"]
        for i in range(self.n_cells):
            fields.append(f"Cell {i+1}")
        with open(self.filename, 'w', newline='') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(fields)

    # logs a line of data to the log file
    def log_data(self, line):
        with open(self.filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(line)

    # gets pressure sensor values, formats into a row, and appends to log file
    def get_sensor_values(self):
        line = [time.time_ns()]
        for i in range(self.n_cells):
            value = self.pressure_val(i)  # call pressure_val(i)
            line.append(value)
            print(line)
            self.log_data(line)

    # gets the value for one pressure sensor
    def pressure_val(self, sensor_id):
        tca_id = sensor_id // 8
        line_id = sensor_id % 4
        value = self.sensor_array[tca_id][line_id].pressure
        return value



    '''
    # whole function is a mess
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
    '''

    def setup_mcp(self, mcp_id, n_pins=16):
        self.mcp[mcp_id] = MCP23017(self.i2c, address=0x20+mcp_id)

        # set all mcp pins to output and init them low/high
        for i in range(n_pins):
            self.mcp_pins[mcp_id][i] = self.mcp[mcp_id].get_pin(i)
            self.mcp_pins[mcp_id][i].switch_to_output(value=True)

            # if mcp_id == 7 4 or 5, drive all pins high (reset and sensor mcp's
            # else drive all pins low
            if (mcp_id == 7) or (mcp_id == 4) or (mcp_id == 5):
                self.mcp_pins[mcp_id][i].value = True
            else:
                self.mcp_pins[mcp_id][i].value = False

    def setup_tca(self, tca_id, n_sensors=8):
        self.tca[tca_id] = adafruit_tca9548a.TCA9548A(self.i2c, address=0x70+tca_id)

    def setup_mpr(self, sensor_id):
        tca_id = sensor_id // 8
        line_id = sensor_id % 8
        print(sensor_id, tca_id, line_id)
        # really not confident this will work
        try:
            self.sensor_array[tca_id][line_id] = adafruit_mprls.MPRLS(self.tca[tca_id][line_id], psi_min=0, psi_max=25)
        except:
            print(f"Sensor # {sensor_id} not working")

    def receive_cmd(self):
        try:
            cmd = self.socket.recv(flags=zmq.NOBLOCK)
            flavor, cell, state, duration = cmd.split()  # put fields here that we want
            # flavor=type of command: direct, pressure
            # cell=cell id
            # state = 0-> nothing, 1-> fill, 2-> empty, or pressure value for pressure control
            # duration = time length of command
            print(cmd)
            return flavor, int(cell), float(state), float(duration)
        except zmq.Again as e:
            print("no cmd received")
            return "empty"

    def receive_actuate_cmd(self):
        return

    def actuate_duration(self, cell_id, state, duration):
        # get solenoid id
        solenoid_id = (cell_id-1)*2 + state
        # get mcp id
        mcp_id = cell_id // 8
        # get mcp pin controlling solenoid
        mcp_pin = solenoid_id % 16
        # set mcp pin to high
        self.mcp_pins[mcp_id][mcp_pin].value = True
        # sleep for the duration
        sleep(duration)
        # set mcp pin to low
        self.mcp_pins[mcp_id][mcp_pin].value = False
        return

    def actuate_pressure(self, cell_id, pressure):
        mcp_id = cell_id // 8
        start = time.time()
        # if desired pressure is greater than current pressure
        if pressure > self.pressure_val(cell_id):
            # get mcp pin
            mcp_pin = ((cell_id-1) % 8) * 2
            # open solenoid valve
            self.mcp_pins[mcp_id][mcp_pin].value = True
            while (self.pressure_val(cell_id) > pressure) and (time.time()-start < 4):
                sleep(0.1)
            self.mcp_pins[mcp_id][mcp_pin].value = False
        else:
            # get mcp pin
            mcp_pin = (cell_id % 8) * 2 - 1
            # open solenoid valve
            self.mcp_pins[mcp_id][mcp_pin].value = True
            while (self.pressure_val(cell_id) > pressure) and (time.time()-start < 4):
                sleep(0.1)
            self.mcp_pins[mcp_id][mcp_pin].value = False
        return

    def fill_all_cells(self):
        for i in range(self.n_cells):
            self.actuate_pressure(i+1, 16.00)
        return


if __name__ == '__main__':
    print("we controlling")
    num_cells = 2
    con = Controller(num_cells)

    while True:
        sleep(1)

    # while True:
    # cycle through stuff here
