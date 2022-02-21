import time
import board
import busio

# i2c expander library
import adafruit_tca9548a
# pressure sensor library
import adafruit_mprls

i2c = busio.I2C(board.SCL, board.SDA)

# create tca object
tca1 = adafruit_tca9548a.TCA9548A(i2c)

mpr1 = adafruit_mprls.MPRLS(tca1[1], psi_min=0, psi_max=25)

while True:
    print((mpr1.pressure,))
    time.sleep(1)
