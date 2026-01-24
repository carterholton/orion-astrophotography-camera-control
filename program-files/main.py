import time
import sys
import os, signal, subprocess
import init
import serial
import logging
from rpi_lcd import LCD
from camera import Camera
from gpiozero import LED
from joystick import Joystick
import focuser
import processing
from startup import Startup
from lcd_tools import Display

log = logging.getLogger("log")
log.setLevel(logging.DEBUG)
stdoutHandler = logging.StreamHandler(stream=sys.stdout)
errHandler = logging.FileHandler("error.log")

stdoutHandler.setLevel(logging.DEBUG)
errHandler.setLevel(logging.ERROR)

fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s")

stdoutHandler.setFormatter(fmt)
errHandler.setFormatter(fmt)

log.addHandler(stdoutHandler)
log.addHandler(errHandler)

log.info("Program started")

lcd = LCD()
joystick = Joystick(lcd, log)
camera = Camera(lcd, log)
preprocess = processing.Preprocess()
led = LED(23)
led.on()

iso = {
0:'AUTO',
1:100,
2:200,
3:400,
4:800,
5:1600,
6:3200,
7:6400,
8:12800}

# dbase is the common database shared between all functions and files. It contains 
dbase = {"Target":"none", "EL":0, "IN":0, "TF":0, "ISO":0, "iso_key":5, "EC":0, "EG":0}

Display = Display()
startup = Startup(Display, dbase, log, joystick, camera)

def killgphoto2Process():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if b'gvfsd-gphoto2' in line:
			pid = int(line.split(None,1) [0])
			os.kill(pid, signal.SIGKILL)

def lcd_update():
    global dbase
    menu = 0
    TF = dbase["TF"]
    IN = dbase["IN"]
    EL = dbase["EL"]
    TFi = TF
    ISO = iso[dbase["iso_key"]]
    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TFi), 2)
    lcd.text("Av: " + str(Av) + " ISO:" + str(ISO), 3)
    if menu == 0:
        est_time = round(((EL+IN) * TFi) / 60)
        est_expo = round((EL * TFi) / 60)
        lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)

def shutter_control():
    global dbase
    time.sleep(1)
    status_id = {"0":"NORMAL", "1a":"BATT LOW", "1b":"DEW POINT", "2a":"BATT DEAD", "2b":"DEW POINT", "2c":"PICO SIGNAL LOST", "3a":"SIGNAL LOST", "3b":"FATAL ERROR"}
    TF = dbase["TF"]
    IN = dbase["IN"]
    EL = dbase["EL"]
    print("TF =",TF)
    TFi = TF
    ISO = iso[dbase["iso_key"]]
    Fnum = 0
    active = True
    mode = "LIGHTS"
    ready = False
    iso_text = 'iso=' + str(dbase["iso_key"])
    camera.set_iso(iso_text)
    Display.static_menu("start")
    while not ready:
        pos = joystick.get_pos()
        if pos[0] == 'up' and pos[1] == '0':
            ready = True
            lcd.clear()
        if pos[0] == 'down' and pos[1] == '0':
            lcd.clear()
            main()
    while active:
        time_left = round((TF * (EL + IN)) / 60)
        camera.capture_image(EL)
        TF = (TF - 1)
        Fnum = (Fnum + 1)
        time_rmng = round((IN * TF) / 60)
        time_left = round((TF * (EL + IN)) / 60)
        Display.progress_bar(TF, TFi, Fnum)
        status = get_status()
        status_label = status_id[status]     
        # Consider moving this to the camera class for simplicity
        if "0" in status:
            wait_val = (EL/2) - 1
            i = 0
            led.on()
            while i < wait_val:
                lcd.text("STATUS: " + status_label, 2)
                time.sleep(2)
                i += 1
        elif "1" in status:
            i = 0
            while i < wait_val:
                time.sleep(1)
                led.off()
                lcd.text("STATUS: " + status_label, 2)
                time.sleep(1)
                led.on()
                lcd.text("STATUS: ", 2)
                i += 1
        elif "2" in status:
            i = 0
            while i < wait_val:
                time.sleep(0.5)
                led.off()
                lcd.text("STATUS: " + status_label, 2)
                time.sleep(0.5)
                led.on()
                lcd.text("STATUS: ", 2)
                time.sleep(0.5)
                led.off()
                lcd.text("STATUS: " + status_label, 2)
                time.sleep(0.5)
                led.on()
                lcd.text("STATUS: ", 2)
                i += 1
        led.off()
        time_left = round((TF * (EL + IN)) / 60)
        joystick.clear_buffer()
        pos = joystick.get_pos()
        print(pos[0])
        if pos[0] == 'down':
            Display.static_menu("paused")
            stick = joystick.get_pos()[0]
            while stick != 'up':
                stick = joystick.get_pos()[0]
            lcd.clear()
        Display.time_status_bar(mode, time_left, status_label)
        time.sleep(IN - 2)
        update_file()
        if TF <= 0:
            Display.static_menu("finished", Fnum, TFi, EL)
            time.sleep(2)
            EL, IN, TF, mode = preprocess.run(dbase, lcd, joystick)
            TFi = TF
            Fnum = 0
            if mode == "DONE":
                break

def get_status():
    batt = camera.battery_level()
    if batt == "low":
        return "1a"
    elif batt == "very low":
        return "2a"
    else:
        return "0"

def update_file():
    global dbase
    dbase["EC"] += round((dbase["EL"]/60), 2)
    data = [("Target: " + dbase["Target"] + "\n"), ("EL: " + str(dbase["EL"]) + "\n"), ("IN: " + str(dbase["IN"]) + "\n"), ("TF: " + str(dbase["TF"]) + "\n"), ("ISO: " + str(dbase["iso_key"]) + "\n"), ("Exposure Minutes: " + str(round(dbase["EC"], 2)) + "\n"), ("Exposure Goal: " + str(round(dbase["EG"], 2)) + "\n")]
    path = "ProjectFiles/" + dbase["Target"] + ".txt"
    with open(path, "w") as file:
        file.writelines(data)

def main():
    global dbase
    killgphoto2Process()
    #dbase = init.run(joystick, log)
    dbase = startup.run()
    #focuser.run(joystick)
    shutter_control()
main()
