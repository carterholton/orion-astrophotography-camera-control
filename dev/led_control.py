import RPi.GPIO as GPIO
import time


class LED:

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	def __init__(self, pin):
		self.pin = pin
		GPIO.setup(self.pin, GPIO.OUT)

	def ON(self):
		GPIO.output(self.pin, GPIO.HIGH)

	def OFF(self):
		GPIO.output(self.pin, GPIO.LOW)

