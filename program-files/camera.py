import os, signal, subprocess
import time

class CameraError(Exception):
	pass

# This class is responsible for handling interfacing with the camera
class Camera:
	def __init__(self, lcd, log):
		self.demo = False
		self.lcd = lcd
		self.log = log

	# this function tests camera connection by sending an arbitrary command and waiting for a response. If the camera does not respond to this command, CameraError is raised and program is halted
	def connect(self, startup=False):
		if not startup:
			self.lcd.clear()
		self.lcd.text("[....] Camera check", 2)
		connected = False
		i = 12
		err_msg = ""
		while (connected == False) and (i > 0):
			try:
				battery_status = subprocess.run(['gphoto2', '--get-config=batterylevel'], capture_output=True,
												text=True)
				output = battery_status.stdout
				level = (output.splitlines())[3].split(" ")
				level = level[1]
				if (level != "100%") and (level != "50%") and (level != "20%"):
					raise Exception
				else:
					connected = True
					break
			except Exception as e:
				err_msg = e
				self.lcd.text("[ERR!] Camera check", 2)
				for j in range(10):
					self.lcd.text(f"Retrying in {10 - j}s...", 4)
					time.sleep(1)
				i -= 1
		if not connected:
			self.lcd.text("[FAIL] Camera check", 2)
			self.lcd.text("FATAL ERROR OCCURRED", 4)
			time.sleep(1)
			self.log.error(err_msg, exc_info=True)
			exit()
		self.lcd.text("[PASS] Camara check", 2)
		self.lcd.text("", 4)

	# Each function below sends a command to the camera using gphoto2
	def open_shutter(self):
		if not self.demo:
			try:
				subprocess.call(['gphoto2', '--set-config', 'eosremoterelease=Immediate', '--wait-event=2s'])
			except:
				self.connect()
		else:
			#print("demo shutter open")
                        duh = 0

	def capture_image(self, EL):
		if not self.demo:
			capture = subprocess.Popen([f"gphoto2 --set-config eosremoterelease=Immediate --wait-event={EL - 1}s --set-config eosremoterelease='Release Full' --wait-event=1s"], stdout=subprocess.PIPE, shell = True, text = True)
			
	def close_shutter(self):
		if not self.demo:
			subprocess.call(['gphoto2 --set-config eosremoterelease="Release Full" --wait-event=2s'], shell = True)
			print("close")
		else:
			#print("demo shutter closed")
                        duh = 0
			
	def set_iso(self, iso_text):
		if not self.demo:
			subprocess.call(['gphoto2', '--set-config',  iso_text])
		else:
			#print("demo set iso")
                        duh = 0

	# This function retrieves the camera's current battery level and converts this value to a corresponding string which is returned to the main program
	def battery_level(self):
		if not self.demo:
			battery_status = subprocess.run(['gphoto2', '--get-config=batterylevel'], capture_output = True, text = True)
			output = battery_status.stdout
			level = (output.splitlines())[3].split(" ")
			level = level[1]
			if level == "50%":
				return("low")
			elif level == "20%":
				return("very low")
			else:
				return("normal")

		else:
			return("low")
