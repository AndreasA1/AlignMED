import time
import csv
import numpy as np
import board
import busio

# components imports
from adafruit_mcp230xx.mcp23017 import MCP23017 #I/O expander library
import adafruit_tca9548a # i2c expander library
import adafruit_mprls # pressure sensor library


class Controller:
    def __init__(self, n_cells):
        print("initializing controller class")

        # initialize class-level values
        self.n_cells = n_cells
        self.cell_states = np.zeros(shape=(2*n_cells,))
        self.cell_state_duration = np.zeros(shape=(2*n_cells,))

        # open file for data logging
        self.filename = f"logs/log_debug.csv"
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

        # i2c bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.setup_i2c()

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
        # setup mcp expanders
        try:
            # mcp expander
        except:
            # try anyways

        # drive reset pins high

        # setup tca objects
        self.tca1 = adafruit_tca9548a.TCA9548A(self.i2c, address=0x70)

        # tie pressure sensors to tca i2c lines
        self.mpr1 = adafruit_mprls.MPRLS(self.tca1[1], psi_min=0, psi_max=25)
        return


if __name__ == '__main__':
    print("we controlling")
    num_cells = 4
    con = Controller(num_cells)