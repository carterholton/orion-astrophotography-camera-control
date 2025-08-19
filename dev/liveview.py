import os, signal, subprocess

while True:
	subprocess.run(["gphoto2 --set-config /main/actions/viewfinder=1"], shell=True)
