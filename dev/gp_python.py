import gphoto2 as gp
import time

camera = gp.Camera()
camera.init()
text = camera.get_summary()
print('Summary')
print('=======')
print(str(text))

for i in range(15):
	camera.capture(0)
	time.sleep(0.5)
#data = camera.get_single_config(camera, "changefarea")
#print(data)
camera.exit()
