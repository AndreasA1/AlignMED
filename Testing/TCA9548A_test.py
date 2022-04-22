import time
import board
import busio

# i2c expander library
import adafruit_tca9548a
# pressure sensor library
import adafruit_mprls

from adafruit_mcp230xx.mcp23017 import MCP23017 #I/O expander library

i2c = busio.I2C(board.SCL, board.SDA)

# create tca object
tca1 = adafruit_tca9548a.TCA9548A(i2c, address=0x70)

mcp = MCP23017(i2c, address=0x24)
mcp0 = mcp.get_pin(0)
mcp1 = mcp.get_pin(1)
mcp2 = mcp.get_pin(2)
mcp3 = mcp.get_pin(3)
mcp4 = mcp.get_pin(4)
mcp5 = mcp.get_pin(5)
mcp6 = mcp.get_pin(6)
mcp7 = mcp.get_pin(7)

mcp0.switch_to_output(value=True)
mcp1.switch_to_output(value=True)
mcp2.switch_to_output(value=True)
mcp3.switch_to_output(value=True)
mcp4.switch_to_output(value=True)
mcp5.switch_to_output(value=True)
mcp6.switch_to_output(value=True)
mcp7.switch_to_output(value=True)

mcp0.value = True
mcp1.value = True
mcp2.value = True
mcp3.value = True
mcp4.value = True
mcp5.value = True
mcp6.value = True
mcp7.value = True

# try:
#     mpr1 = adafruit_mprls.MPRLS(tca1[0], psi_min=0, psi_max=25)
# except:
#     print("1")
# try:
#     mpr2 = adafruit_mprls.MPRLS(tca1[1], psi_min=0, psi_max=25)
# except:
#     print("2")
try:
    mpr3 = adafruit_mprls.MPRLS(tca1[2], psi_min=0, psi_max=25)
except:
    print("3")
# try:
#     mpr4 = adafruit_mprls.MPRLS(tca1[3], psi_min=0, psi_max=25)
# except:
#     print("4")
# try:
#     mpr5 = adafruit_mprls.MPRLS(tca1[4], psi_min=0, psi_max=25)
# except:
#     print("5")
# try:
#     mpr6 = adafruit_mprls.MPRLS(tca1[5], psi_min=0, psi_max=25)
# except:
#     print("6")
# try:
#     mpr7 = adafruit_mprls.MPRLS(tca1[6], psi_min=0, psi_max=25)
# except:
#     print("7")
# try:
#     mpr8 = adafruit_mprls.MPRLS(tca1[7], psi_min=0, psi_max=25)
# except:
#     print("8")


while True:
    # print((mpr1.pressure,))
    # print(f"Pressure Sensor 1: {mpr1.pressure}")
    # print(f"Pressure Sensor 2: {mpr2.pressure}")
    print(f"Pressure Sensor 3: {mpr3.pressure}")
    # print(f"Pressure Sensor 4: {mpr4.pressure}")
    # print(f"Pressure Sensor 5: {mpr5.pressure}")
    # print(f"Pressure Sensor 6: {mpr6.pressure}")
    # print(f"Pressure Sensor 7: {mpr7.pressure}")
    # print(f"Pressure Sensor 8: {mpr8.pressure}")
    time.sleep(1)
