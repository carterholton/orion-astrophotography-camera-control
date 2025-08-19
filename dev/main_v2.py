import time
import os, signal, subprocess
import readchar
import init
from rpi_lcd import LCD
from camera import Camera
from led_control import LED
lcd = LCD()
camera = Camera()
RED = LED(23)
RED.OFF()

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

dbase = {"Target":"none", "EL":0, "IN":0, "TF":0, "ISO":0, "iso_key":5, "Taken":0}

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
    #pause()

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
    lcd.text("Press 0 to begin", 2)
    lcd.text("Press '=' to reboot", 4)
    while not ready:
        if readchar.readkey() == '0':
            ready = True
            lcd.clear()
    while True:
        if kill2 == 0:
            if pause == 0:
                print("control triggered")
                print(TFi)
                camera.open_shutter()
                TF = (TF - 1)
                Fnum = (Fnum + 1)
                time_rmng = round((IN * TF) / 60)
                percent = ((str(round(100 * (((TFi - TF) / TFi))))) + "%")
                progress = (((TFi - TF) / TFi) * 14)
                shots_left = (TFi - Fnum)
                print(progress)
                empty_progress = (14 - progress)
                bar_filled = ""
                bar_unfilled = ""
                while progress > 0:
                    bar_filled = (bar_filled + "*")
                    progress = (progress - 1)
                while empty_progress > 0:
                    bar_unfilled = (bar_unfilled + " ")
                    empty_progress = (empty_progress - 1)
                lcd.text(percent + "[" + bar_filled + bar_unfilled + "]", 4)
                status = get_status()
                status_label = status_id[status]
                if "0" in status:
                    while i <= EL/2:
                        RED.ON()
                        lcd.text("STATUS: " + status_label, 2)
                        time.sleep(2)
                if "1" in status:
                    i = 0
                    while i <= EL/2:
                        time.sleep(1)
                        RED.OFF()
                        lcd.text("STATUS: " + status_label, 2)
                        time.sleep(1)
                        RED.ON()
                        lcd.text("STATUS: ", 2)
                        i += 1
                if "2" in status:
                    i = 0
                    while i <= EL/2:
                        time.sleep(0.5)
                        RED.OFF()
                        lcd.text("STATUS: " + status_label, 2)
                        time.sleep(0.5)
                        RED.ON()
                        lcd.text("STATUS: ", 2)
                        time.sleep(0.5)
                        RED.OFF()
                        lcd.text("STATUS: " + status_label, 2)
                        time.sleep(0.5)
                        RED.ON()
                        lcd.text("STATUS: ", 2)
                        i += 1
                camera.close_shutter()
                RED.OFF()
                time_left = round((TF * (EL + IN)) / 60)
                lcd.text(">ACTIVE:" + str(time_left) + " min left<", 1)
                lcd.text("STATUS: " + status_label, 2)
                time.sleep(IN)
                update_file()
                if TF <= 0:
                    lcd.clear()
                    lcd.text("Captured " + str(Fnum) + " Photos!", 1)
                    lcd.text("Total EXP: " + str(round((TFi * EL) / 60)) + "min", 2)
                    if darks == 0:
                        lcd.text("Capture Dark Frames?", 3)
                        lcd.text("    4)Yes   5)No    ", 4)
                        while True:
                            lcd.clear()
                            GREEN.ON()
                            if readchar.readkey() == '4' or '5':
                                if readchar.readkey() == '4':
                                    lcd.clear()
                                    lcd.text("Capturing Darks", 2)
                                    print("read 4")
                                    TF = 30
                                    TFi = 30
                                    IN = 5
                                    Fnum = 0
                                    darks = 1
                                    break
                                if keyboard.read_key() == '5':
                                    kill1 = 1
                                    break
                    else:
                        kill2 = 1
                        print("elsekill")


            else:
                if menu == 1:
                    break
                    print("elsemenu")
            print("else")

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
    dbase["Taken"] = dbase["Taken"] + 1
    print("shots this time: ", dbase["Taken"])
    data = [("Target: " + dbase["Target"] + "\n"), ("EL: " + str(EL) + "\n"), ("IN: " + str(IN) + "\n"), ("TF: " + str(dbase["TF"]) + "\n"), ("ISO: " + str(dbase["iso_key"]) + "\n"), ("Shots taken: " + str(dbase["Taken"]) + "\n")]
    print(data)
    path = "ProjectFiles/" + dbase["Target"] + ".txt"
    with open(path, "w") as file:
        file.writelines(data)

def main():
    global dbase
    killgphoto2Process()
    dbase = init.run()
    shutter_control()
"""
except Exception as e:
        lcd.clear()
        lcd.text("ERROR OCCURRED", 1)
        lcd.text("REBOOTING IN 5s", 2)
        time.sleep(5)
        main()
""" 
main()


