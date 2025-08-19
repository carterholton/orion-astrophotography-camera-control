import os, subprocess
import readchar
import time
from rpi_lcd import LCD
lcd = LCD()
import joystick

def screen():
    lcd.clear()
    #lcd.text("                    ")
    lcd.text(" Use Stick to Focus ",1)
    lcd.text(" SPEED: 3 ",4)


def run(stick):
    global joystick
    joystick = stick
    screen()
    subprocess.call(['gphoto2', '--set-config-value', '/main/actions/viewfinder=1'])
    time.sleep(5)
    ready = False
    speed = '3'
    while ready != True:
        joystick.clear_buffer()
        pos = joystick.get_pos()
        if pos[0] == 'left':
            subprocess.call([f'gphoto2 --set-config manualfocusdrive="Near {speed}"'], shell=True)
        if pos[0] == 'right':
            subprocess.call([f'gphoto2 --set-config manualfocusdrive="Far {speed}"'], shell=True)
        if pos[0] == 'up':
            if speed == '3':
                speed = '1'
                lcd.text(" SPEED: 1",4)
                time.sleep(0.5)
            elif speed == '1':
                speed = '3'
                lcd.text( "SPEED: 3",4)
                time.sleep(0.5)
        if pos[1] == '0':
            ready = True
            subprocess.call(['gphoto2', '--set-config-value', '/main/actions/viewfinder=0'])

#WORKING PROGRAM THAT CHANGES FOCUS WITH LIVEVIEW ON
#SD CARD NOT IN CAMERA
