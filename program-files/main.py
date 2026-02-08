import time
import sys
import os, signal, subprocess
import init
import serial
import logging
import threading
import queue
from rpi_lcd import LCD
from camera import Camera
from gpiozero import LED
from joystick import Joystick
import focuser
import processing
from startup import Startup
from lcd_tools import Display, DynamicMenu
from led_tools import Led

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
led_stop = threading.Event()
menu_stop = threading.Event()
Led = Led(led, led_stop)
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
menu_queue = queue.Queue()
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
    menu = DynamicMenu(joystick,
                                 menu_queue,
                                 menu_stop,
                                 menu_items=["Option 0", "Option 1", "Option 2"],
                                 submenu_items=[["Sub0 Op0", "Sub0 Op1"], ["Sub1 Op0", "Sub1 Op1", "Sub1 Op2"], []]
                                 )
    menu_thread = threading.Thread(target=menu.run)

    while not ready:
        pos = joystick.get_pos()
        if pos[0] == 'up' and pos[1] == '0':
            ready = True
            lcd.clear()
        if pos[0] == 'down' and pos[1] == '0':
            lcd.clear()
            main()
    menu_thread.start()
    menu_active = False

    while active:
        start_time = time.perf_counter()
        elapsed_time = 0
        TF = (TF - 1)
        Fnum = (Fnum + 1)
        if not menu_active:
            lcd.clear()
            Display.progress_bar(TF, TFi, Fnum, line=4)
        status = get_status()
        status_label = status_id[status]
        camera.capture_image(EL, IN)
        status_light = threading.Thread(target=Led.status_light, args=("0", EL), daemon=True)
        status_light.start()
        while elapsed_time < EL:
            elapsed_time = time.perf_counter() - start_time
            try:
                value = menu_queue.get_nowait()
                print("Got:", value)
            except queue.Empty:
                value = ""
            if value == "active":
                menu_active = True
            elif value != "":
                menu_active = False
        """
        if pos[0] == 'down':
            lcd.clear()
            lcd.text("   SHOOTING PAUSED   ", 2)
            lcd.text("   >UP to resume<    ", 3)
            stick = joystick.get_pos()[0]
            while stick != 'up':
                stick = joystick.get_pos()[0]
            lcd.clear()
        if mode == "LIGHTS":
            lcd.text(">ACTIVE:" + str(time_left) + " min left<", 1)
        if mode == "DARKS":
            lcd.text(">DARKS:" + str(time_left) + " min left<", 1)
        lcd.text("STATUS: " + status_label, 2)
        # print("STATUS: " + status_label + "  >> " + str(time_left) + " minutes remaining << ", end="\r")
        """
        time.sleep(IN)
        led_stop.set()
        status_light.join()
        led_stop.clear()
        update_file()
        if TF <= 0:
            menu_stop.set()
            menu_thread.join()
            lcd.clear()
            lcd.text("Captured " + str(Fnum) + " Photos!", 1)
            lcd.text("Total EXP: " + str(round((TFi * EL) / 60)) + "min", 2)
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
