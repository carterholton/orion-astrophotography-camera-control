import time
import os, signal, subprocess
import readchar
import init
import serial
from rpi_lcd import LCD
from camera import Camera
from gpiozero import LED
from joystick import Joystick
import focuser

joystick = Joystick()
lcd = LCD()
camera = Camera()
led = LED(23)
led.on()

"""
line1 = "  __   __ .  _   _  "
line2 = " |  | |   | | | | | "
line3 = " |__| |   | |_| | | "

end = -20
for i in range(20):
    lcd.text(line1[:end], 1)
    lcd.text(line2[:end], 2)
    lcd.text(line3[:end], 3)
    end += 1
    time.sleep(0.0001)

time.sleep(1)
"""

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

def killgphoto2Process():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if b'gvfsd-gphoto2' in line:
			pid = int(line.split(None,1) [0])
			os.kill(pid, signal.SIGKILL)

def lcd_update():
    global TF
    global IN
    global EL
    global TFi
    global iso
    global iso_key
    global Av
    global lcd
    global menu
    global dbase
    menu = 0;
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
    global menu
    menu = 1
    while True:
        if menu == 1:
            break
    time.sleep(1)
    global TF
    global IN
    global lcd
    global EL
    global TFi
    global iso
    global iso_key
    global kill2
    global pause
    menu = 0;
    status_id = {"0":"NORMAL", "1a":"BATT LOW", "1b":"DEW POINT", "2a":"BATT DEAD", "2b":"DEW POINT", "2c":"PICO SIGNAL LOST", "3a":"SIGNAL LOST", "3b":"FATAL ERROR"}
    TF = dbase["TF"]
    IN = dbase["IN"]
    EL = dbase["EL"]
    print("TF =",TF)
    TFi = TF
    ISO = iso[dbase["iso_key"]]
    kill2 = 0
    pause = 0
    Fnum = 0
    alternate = 0
    darks = 0
    lcd.clear()
    ready = False;
    iso_text = 'iso=' + str(dbase["iso_key"])
    camera.set_iso(iso_text)
    lcd.text(">SYSTEM READY<", 1)
    lcd.text("Press 'UP' to begin", 2)
    lcd.text("Press 'DWN' to reboot", 4)
    while not ready:
        pos = joystick.get_pos()
        if pos[0] == 'up' and pos[1] == '0':
            ready = True
            lcd.clear()
        if pos[0] == 'down' and pos[1] == '0':
            lcd.clear()
            main()
    while True:
        if kill2 == 0:
            if pause == 0:
                #print("control triggered")
                #print(TFi)
                capture = subprocess.Popen([f"gphoto2 --set-config eosremoterelease=Immediate --wait-event={EL}s --set-config eosremoterelease='Release Full'"], stdout=subprocess.PIPE, shell = True, text = True)
                TF = (TF - 1)
                Fnum = (Fnum + 1)
                time_rmng = round((IN * TF) / 60)
                percent = ((str(round(100 * (((TFi - TF) / TFi))))) + "%")
                progress = (((TFi - TF) / TFi) * 14)
                shots_left = (TFi - Fnum)
                #print(progress)
                empty_progress = (14 - progress)
                bar_filled = ""
                bar_unfilled = ""
                p_bar_filled = ""
                p_bar_unfilled = ""
                while progress > 0:
                    bar_filled = (bar_filled + "*")
                    p_bar_filled = (p_bar_filled + "█")
                    progress = (progress - 1)
                while empty_progress > 0:
                    bar_unfilled = (bar_unfilled + " ")
                    p_bar_unfilled = (p_bar_unfilled + "-")
                    empty_progress = (empty_progress - 1)
                lcd.text(percent + "[" + bar_filled + bar_unfilled + "]", 4)
                print(percent + " [" + p_bar_filled*6 + p_bar_unfilled*6 + "]", end="\r")
                status = get_status()
                status_label = status_id[status]
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
                capture.communicate()
                #killgphoto2Process()
                #print("killed process")
                led.off()
                time_left = round((TF * (EL + IN)) / 60)
                #print()
                joystick.clear_buffer()
                pos = joystick.get_pos()
                print(pos[0])
                if pos[0] == 'down':
                    lcd.clear()
                    lcd.text("   SHOOTING PAUSED   ", 2)
                    lcd.text("   >UP to resume<    ", 3)
                    while joystick.get_pos()[0] != 'up':
                        pause = 0
                    lcd.clear()
                if darks == 0:
                    lcd.text(">ACTIVE:" + str(time_left) + " min left<", 1)
                else:
                    lcd.text(">DARKS:" + str(time_left) + " min left<", 1)
                lcd.text("STATUS: " + status_label, 2)
                print("STATUS: " + status_label + "  >> " + str(time_left) + " minutes remaining << ", end="\r")
                time.sleep(IN - 2)
                update_file()
                if TF <= 0:
                    lcd.clear()
                    lcd.text("Captured " + str(Fnum) + " Photos!", 1)
                    lcd.text("Total EXP: " + str(round((TFi * EL) / 60)) + "min", 2)
                    if darks == 0:
                        lcd.clear()
                        lcd.text("Capture Dark Frames?", 3)
                        lcd.text("   UP)Yes   DN)No   ", 4)
                        while True:
                            pos = joystick.get_pos()
                            if pos[0] == 'up' or 'down':
                                if pos[0] == 'up':
                                    lcd.clear()
                                    lcd.text("Capturing Darks", 2)
                                    TF = 30
                                    TFi = 30
                                    IN = 5
                                    Fnum = 0
                                    darks = 1
                                    break
                                if pos[0] == 'down':
                                    kill1 = 1
                                    break
                    else:
                        kill2 = 1
                        print("elsekill")


            else:
                if menu == 1:
                    break
                    print("elsemenu")
            #print("else")

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
    global EL
    global IN
    global TF
    global TFi
    dbase["EC"] += round((EL/60), 2)
    #print("shots this time: ", dbase["Taken"])
    data = [("Target: " + dbase["Target"] + "\n"), ("EL: " + str(EL) + "\n"), ("IN: " + str(IN) + "\n"), ("TF: " + str(dbase["TF"]) + "\n"), ("ISO: " + str(dbase["iso_key"]) + "\n"), ("Exposure Minutes: " + str(round(dbase["EC"], 2)) + "\n"), ("Exposure Goal: " + str(round(dbase["EG"], 2)) + "\n")]
    #print(data)
    path = "ProjectFiles/" + dbase["Target"] + ".txt"
    with open(path, "w") as file:
        file.writelines(data)

def main():
    global dbase
    killgphoto2Process()
    dbase = init.run(joystick)
    focuser.run(joystick)
    shutter_control()
main()


