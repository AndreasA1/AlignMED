import time
import board
import busio
import digitalio

from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)

mcp0 = MCP23017(i2c, address=0x20)

mcp0_pin0 = mcp0.get_pin(0)

mcp0_pin0.switch_to_output(value=True)

while True:
    #blink pin 0
    mcp0_pin0.value = True
    time.sleep(0.5)
    mcp0_pin0.value = False
    time.sleep(0.5)
    print("we loopin")
