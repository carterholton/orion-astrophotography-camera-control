import os, subprocess
import readchar
import time
from rpi_lcd import LCD
lcd = LCD()

def run():
    lcd.clear()
    #lcd.text("                    ")
    lcd.text("Use Keypad to Focus ",1)
    lcd.text(" <<<4 <5 || 6> +>>> ",3)
    lcd.text("       Center       ",4)

run()


def focuser():
    subprocess.call(['gphoto2', '--set-config-value', '/main/actions/viewfinder=1'])
    time.sleep(5)
    while True:
        subprocess.call(['gphoto2 --set-config manualfocusdrive="Far 3"'], shell=True)
        time.sleep(2)

focuser()

#WORKING PROGRAM THAT CHANGES FOCUS WITH LIVEVIEW ON
#SD CARD NOT IN CAMERA
