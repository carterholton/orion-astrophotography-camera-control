import os, signal, subprocess

class CameraError(Exception):
	pass

class Camera:
	def __init__(self):
		self.demo = False

	def test(self):
		try:
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
		except:
			exit()

	def open_shutter(self):
		if not self.demo:
			subprocess.call(['gphoto2', '--set-config', 'eosremoterelease=Immediate', '--wait-event=2s'])
			print("open")
		else:
			#print("demo shutter open")
                        duh = 0

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
