import os, signal, subprocess

class CameraError(Exception):
	pass

# This class is responsible for handling interfacing with the camera
class Camera:
	def __init__(self):
		self.demo = False

	# this function tests camera connection by sending an arbitrary command and waiting for a response. If the camera does not respond to this command, CameraError is raised and program is halted
	def test(self):
		print("Testing connection...", end="")
		battery_status = subprocess.run(['gphoto2', '--get-config=batterylevel'], capture_output = True, text = True)
		output = battery_status.stdout
		level = (output.splitlines())[3].split(" ")
		level = level[1]
		if (level != "100%") and (level != "50%") and (level != "20%"):
			print("ERROR")
			print("Connection could not be established!\n")
			print(output)
			raise CameraError("camera must properly connected and powered on")
		print("working")
		return 0

	# Each function below sends a command to the camera using gphoto2
	def open_shutter(self):
		if not self.demo:
			subprocess.call(['gphoto2', '--set-config', 'eosremoterelease=Immediate', '--wait-event=2s'])
			print("open")
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
