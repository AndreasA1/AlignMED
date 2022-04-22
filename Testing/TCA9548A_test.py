import time
import board
import busio

# i2c expander library
import adafruit_tca9548a
# pressure sensor library
import adafruit_mprls

i2c = busio.I2C(board.SCL, board.SDA)

# create tca object
tca1 = adafruit_tca9548a.TCA9548A(i2c, address=0x70)

mpr1 = adafruit_mprls.MPRLS(tca1[0], psi_min=0, psi_max=25)
mpr2 = adafruit_mprls.MPRLS(tca1[1], psi_min=0, psi_max=25)
mpr3 = adafruit_mprls.MPRLS(tca1[2], psi_min=0, psi_max=25)
mpr4 = adafruit_mprls.MPRLS(tca1[3], psi_min=0, psi_max=25)
mpr5 = adafruit_mprls.MPRLS(tca1[4], psi_min=0, psi_max=25)
mpr6 = adafruit_mprls.MPRLS(tca1[5], psi_min=0, psi_max=25)
mpr7 = adafruit_mprls.MPRLS(tca1[6], psi_min=0, psi_max=25)
mpr8 = adafruit_mprls.MPRLS(tca1[7], psi_min=0, psi_max=25)

while True:
    # print((mpr1.pressure,))
    print(f"Pressure Sensor 1: {mpr1.pressure}")
    print(f"Pressure Sensor 2: {mpr2.pressure}")
    print(f"Pressure Sensor 3: {mpr3.pressure}")
    print(f"Pressure Sensor 4: {mpr4.pressure}")
    print(f"Pressure Sensor 5: {mpr5.pressure}")
    print(f"Pressure Sensor 6: {mpr6.pressure}")
    print(f"Pressure Sensor 7: {mpr7.pressure}")
    print(f"Pressure Sensor 8: {mpr8.pressure}")
    time.sleep(1)
