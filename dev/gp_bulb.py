import os, signal, subprocess
import time

subprocess.run(["gphoto2 --set-config capturetarget=1 --wait-event=1s"], shell = True)

for i in range(10):
	#data = subprocess.run(["gphoto2 --set-config eosremoterelease=Immediate --wait-event=5s --set-config eosremoterelease='Release Full'"], capture_output = True, text = True, shell = True)
	EL = 5
	capture = subprocess.Popen([f"gphoto2 --set-config eosremoterelease=Immediate --wait-event={EL}s --set-config eosremoterelease='Release Full'"], stdout=subprocess.PIPE, shell = True, text = True)
	print("done")
	time.sleep(5)
	print("5 seconds")
	time.sleep(5)
	print("10 seconds")
	capture.communicate()


