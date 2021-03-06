import time
import csv
import numpy as np
import board
import busio

# components imports
from adafruit_mcp230xx.mcp23017 import MCP23017  # I/O expander library
import adafruit_tca9548a  # i2c expander library
import adafruit_mprls  # pressure sensor library file

import sys
import zmq

from time import sleep


class Controller:
    def __init__(self, n_cells):
        print("initializing controller class")
        self.cutoff_pressure = 14.95  # psi
        self.cutoff_time = 10  # seconds

        self.cutoff_pressure_high = 15.5  # psi

        self.middle_cells = [13, 14, 15, 16, 17, 18]

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
        self.setup_tca()

        self.broken_sensors = []
        # init pressure sensors
        for i in range(n_cells):
            print(f"mpr: {i}")
            self.setup_mpr(i)

        self.init_log_file()
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
        line = [time.time()]
        for i in range(self.n_cells):
            value = self.pressure_val(i)  # call pressure_val(i)
            sleep(0.05)
            line.append(value)
        # print(line)
        self.log_data(line)

    # gets the value for one pressure sensor
    def pressure_val(self, sensor_id):
        tca_id = sensor_id // 8
        line_id = sensor_id % 8
        if line_id == 2:
            line_id = 7
        elif line_id == 3:
            line_id = 6
        elif line_id == 4:
            line_id = 5
        elif line_id == 5:
            line_id = 4
        elif line_id == 6:
            line_id = 3
        elif line_id == 7:
            line_id = 2

        print(f"Sensor {sensor_id+1} at tca {tca_id} line {line_id}")
        try:
            value = 0.0145037738 * self.sensor_array[tca_id][line_id].pressure
        except:
            print(f"Sensor {sensor_id+1} unable to return value")
            value = 14.8
        return value

    def setup_mcp(self, mcp_id, n_pins=16):
        self.mcp[mcp_id] = MCP23017(self.i2c, address=0x20+mcp_id)

        # set all mcp pins to output and init them low/high
        for i in range(n_pins):
            self.mcp_pins[mcp_id][i] = self.mcp[mcp_id].get_pin(i)
            self.mcp_pins[mcp_id][i].switch_to_output(value=True)

            # if mcp_id == 7, drive all pins high (reset and sensor mcp's
            # else drive all pins low
            if mcp_id == 7:
                self.mcp_pins[mcp_id][i].value = True
            elif (mcp_id == 4) or (mcp_id == 5): #reset all pressure sensors
                self.mcp_pins[mcp_id][i].value = True
                self.mcp_pins[mcp_id][i].value = False
                sleep(0.001)
                self.mcp_pins[mcp_id][i].value = True
            else: # turn off all solenoid pins
                self.mcp_pins[mcp_id][i].value = False

    def setup_tca(self):
        self.tca[0] = adafruit_tca9548a.TCA9548A(self.i2c, address=0x71)
        self.tca[1] = adafruit_tca9548a.TCA9548A(self.i2c, address=0x70)
        self.tca[2] = adafruit_tca9548a.TCA9548A(self.i2c, address=0x73)
        self.tca[3] = adafruit_tca9548a.TCA9548A(self.i2c, address=0x72)

    def setup_mpr(self, sensor_id):
        tca_id = sensor_id // 8
        line_id = sensor_id % 8
        # switch line id
        if line_id == 2:
            line_id = 7
        elif line_id == 3:
            line_id = 6
        elif line_id == 4:
            line_id = 5
        elif line_id == 5:
            line_id = 4
        elif line_id == 6:
            line_id = 3
        elif line_id == 7:
            line_id = 2

        print(sensor_id+1, tca_id, line_id)
        try:
            self.sensor_array[tca_id][line_id] = adafruit_mprls.MPRLS(self.tca[tca_id][line_id], psi_min=0, psi_max=25)
            sleep(0.1)
        except:
            print(f"Sensor # {sensor_id+1} not working")
            self.broken_sensors.append(sensor_id+1)
            sleep(0.1)

    def reset_mpr(self, sensor_id):
        mcp_id = (sensor_id // 16) + 4
        mcp_pin = sensor_id % 16
        self.mcp_pins[mcp_id][mcp_pin].value = True
        self.mcp_pins[mcp_id][mcp_pin].value = False
        sleep(0.001)
        self.mcp_pins[mcp_id][mcp_pin].value = True
        return

    '''
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
    '''

    def actuate_duration(self, cell_id, state, duration, p_thresh):
        if p_thresh == 'high':
            p_limit = self.cutoff_pressure_high
        elif p_thresh == 'nolim':
            p_limit = 25
        else:
            p_limit = self.cutoff_pressure

        # get sensor id
        sensor_id = cell_id-1

        # cell 16 was moved to place 31
        if cell_id == 16:
            cell_id = 31
        solenoid_id = (cell_id-1)*2 + state
        # get mcp id
        mcp_id = (cell_id-1) // 8
        # get mcp pin controlling solenoid
        mcp_pin = (solenoid_id-1) % 16

        print(f"actuating cell {cell_id}")
        print(f"mcp id: {mcp_id}")
        print(f"mcp_pin: {mcp_pin}")

        # set mcp pin to high
        self.mcp_pins[mcp_id][mcp_pin].value = True
        start = time.time()

        p_val = self.pressure_val(sensor_id)
        # sleep for the duration while checking for cutoff pressure
        while (p_val < p_limit) and (time.time()-start < duration):
            sleep(0.1)
            p_val = self.pressure_val(sensor_id)
            print(p_val)
        # set mcp pin to low
        self.mcp_pins[mcp_id][mcp_pin].value = False
        print("done")
        return

    def actuate_pressure(self, cell_id, pressure):
        # get sensor id
        sensor_id = cell_id-1

        #  since cell 16 is messed up
        if cell_id == 16:
            cell_id = 31
        mcp_id = (cell_id-1) // 8
        start = time.time()

        # if desired pressure is greater than current pressure
        if pressure > self.pressure_val(sensor_id):  # open inlet
            state = 1
            # get mcp pin
            solenoid_id = (cell_id-1)*2 + state
            mcp_pin = (solenoid_id-1) % 16
            # open solenoid valve
            self.mcp_pins[mcp_id][mcp_pin].value = True
            while (pressure > self.pressure_val(sensor_id)) and (time.time()-start < self.cutoff_time):
                sleep(0.1)
            self.mcp_pins[mcp_id][mcp_pin].value = False
        else:  # open outlet
            state = 2
            # get mcp pin
            solenoid_id = (cell_id-1)*2 + state
            mcp_pin = (solenoid_id-1) % 16
            # open solenoid valve
            self.mcp_pins[mcp_id][mcp_pin].value = True
            while (self.pressure_val(sensor_id) > pressure) and (time.time()-start < self.cutoff_time):
                sleep(0.1)
            self.mcp_pins[mcp_id][mcp_pin].value = False
        return

    def fill_all_cells(self):
        for i in range(self.n_cells):
            cell_id = i+1
            if cell_id not in self.broken_sensors:
                self.actuate_pressure(cell_id, self.cutoff_pressure)
        return

    def fill_middle_cells(self):
        for i in self.middle_cells:
            cell_id = i
            if cell_id not in self.broken_sensors:
                self.actuate_pressure(cell_id, self.cutoff_pressure_high)
        return


if __name__ == '__main__':
    print("we controlling")
    num_cells = 30
    con = Controller(num_cells)

    while True:
        sleep(1)

    # while True:
    # cycle through stuff here
