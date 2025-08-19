import RPi.GPIO as GPIO
import time
from led_control import LED

GREEN = LED(23)
YELLOW = LED(24)
RED = LED(23) 

while True:
    RED.ON()
    time.sleep(0.5)
    RED.OFF()
    time.sleep(0.5)
