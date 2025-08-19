import os, signal, subprocess

battery_status = subprocess.run(['gphoto2', '--get-config=batterylevel'], capture_output = True, text = True)
output = battery_status.stdout
level = (output.splitlines())[3].split(" ")
level = level[1]
print("running script!")
print(level)
