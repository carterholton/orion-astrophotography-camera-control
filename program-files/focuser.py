#This module runs both the UI and hardware interfacing for camera focus control

import os, subprocess
import time
from rpi_lcd import LCD
lcd = LCD()
import joystick

# This function displays user instructions for focusing on the LCD display
def screen():
    lcd.clear()
    #lcd.text("                    ")
    lcd.text(" Use Stick to Focus ",1)
    lcd.text(" SPEED: 3 ",4)

# This function uses input from the Arduino joystick to adjust camera focus
def run(stick):
    global joystick
    joystick = stick
    # display instructions on LCD 
    screen()
    # Open the camera liveview (necessary for focusing)
    subprocess.call(['gphoto2', '--set-config-value', '/main/actions/viewfinder=1'])
    time.sleep(5)
    ready = False
    # Sets the default focusing speed: 3 = fastest, 2 = medium, 1 = slowest
    speed = '3'
    while ready != True:
        # clear serial buffer and retrieve current joystick position
        joystick.clear_buffer()
        pos = joystick.get_pos()
        # if joystick is pointed left, focus nearer
        if pos[0] == 'left':
            subprocess.call([f'gphoto2 --set-config manualfocusdrive="Near {speed}"'], shell=True)
        # if joystick is pointed right, focus further out
        if pos[0] == 'right':
            subprocess.call([f'gphoto2 --set-config manualfocusdrive="Far {speed}"'], shell=True)
         # if joystick pointed up, switch focus speed
        if pos[0] == 'up':
            if speed == '3':
                speed = '1'
                lcd.text(" SPEED: 1",4)
                time.sleep(0.5)
            elif speed == '1':
                speed = '3'
                lcd.text( "SPEED: 3",4)
                time.sleep(0.5)
        # when joystick is pressed, exit focus tool
        if pos[1] == '0':
            ready = True
            subprocess.call(['gphoto2', '--set-config-value', '/main/actions/viewfinder=0'])

#WORKING PROGRAM THAT CHANGES FOCUS WITH LIVEVIEW ON
#SD CARD NOT IN CAMERA
