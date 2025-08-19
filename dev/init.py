
from rpi_lcd import LCD
lcd = LCD()
import readchar
import time
from camera import Camera
import os
camera = Camera()

dbase = {"Target":"empty", "EL":0, "IN":0, "TF":0, "iso_key":5, "EC":0, "EG":0}

iso_index = {
0:'AUTO',
1:100,
2:200,
3:400,
4:800,
5:1600,
6:3200,
7:6400,
8:12800}

def system_check():
    global dbase
    lcd.clear()
    lcd.text("[....] System check", 1)
    time.sleep(1)
    lcd.text("[PASS] System check", 1)
    lcd.text("[....] Camera check", 2)
    time.sleep(1)
    result = camera.test()
    if result == 0:
        lcd.text("[PASS] Camera check", 2)
    else:
        lcd.text("[FAIL] Camera check", 2)
        return 1
    lcd.text("[....] Input check", 3)
    input()
    lcd.text("[PASS] Input check", 3)
    lcd.text("ALL CHECKS PASSED!", 4)
    time.sleep(2)
    lcd.clear()
    return 0

def run():
    global dbase
    """
    lcd.text("Smart", 4)
    time.sleep(1)
    lcd.text("Smart Camera", 4)
    time.sleep(1)
    lcd.text("Smart Camera System ", 4)
    time.sleep(4)
    """
    if system_check() == 1:
        lcd.text("FATAL ERROR OCCURED!" , 4)
        while True:
            val = 0
    lcd.text("      ORION CC      ",1)
    lcd.text("1) Load Project     ",3)
    lcd.text("2) Custom Shoot     ",4)
    no_selection = True
    while no_selection:
        key = readchar.readkey()
        if key == '1':
            load_project()
            no_selection = False
        elif key == '2':
            update = {"Target":"Custom"}
            dbase = {**dbase, **update}
            cam_config()
            no_selection = False
    return dbase

def load_project():
    global dbase
    lcd.clear()
    lcd.text("  Choose a project  ",2)
    lcd.text("   From the list:   ",3)
    time.sleep(2)
    lcd.clear()
    file_list = os.listdir("ProjectFiles")
    i = 0
    for file in file_list:
        if i <= 4:
            name = file.rsplit('.',1)[0]
            #print(name)
            i += 1
            lcd.text(str(i) + ") " + name, i)
    no_selection = True
    while no_selection:
        key = readchar.readkey()
        if key == '1':
            proj_index = 1
            no_selection = False
        elif key == '2':
            proj_index = 2
            no_selection = False
        elif key == '3':
            proj_index = 3
            no_selection = False
        elif key == '4':
            proj_index = 4
            no_selection = False
    project = "ProjectFiles/" + file_list[proj_index - 1]
    with open(project, 'r') as file:
        lines = file.readlines()
        target = (lines[0].split(': ',1)[1]).strip()
        EL = (lines[1].split(': ',1)[1]).strip()
        IN = (lines[2].split(': ',1)[1]).strip()
        TF = (lines[3].split(': ',1)[1]).strip()
        iso_key = (lines[4].split(': ',1)[1]).strip()
        expo_cap = (lines[5].split(': ',1)[1]).strip()
        expo_goal = (lines[6].split(': ',1)[1]).strip()

        dbase = {"Target":target, "EL":int(EL), "IN":int(IN), "TF":int(TF), "iso_key":int(iso_key), "EC":float(expo_cap), "EG":float(expo_goal)}
        cam_config()

def cam_config():
    #try:
    if True:
        global dbase
        global iso_index
        lcd.clear()
        lcd.text("Booting...", 2)
        time.sleep(2)
        lcd.clear()
        EL = dbase["EL"]
        IN = dbase["IN"]
        TF = dbase["TF"]
        iso_key = dbase["iso_key"]
        #lcd.text("TARGET: " + dbase["Target"] + " (" + (str(round((dbase["EC"]/dbase["EG"])*100))) + "%)", 1)
        percent = (round((dbase["EC"]/dbase["EG"])*100))
        lcd.text(dbase["Target"] + "("+ str(percent) + "->" + str(round(((dbase["EC"] + (EL*TF/60)) / dbase["EG"]) * 100)) + "%)", 1)
        #percent = (round((dbase["EC"]/dbase["EG"])*100))
        Flag = False
        first = 1
        ISO = iso_index[iso_key]
        lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF), 2)
        lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
        est_time = round(((EL+IN) * TF) / 60)
        est_expo = round((EL * TF) / 60)
        lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)
        while not Flag:
            key = readchar.readkey().strip()
            if (key == '7' or '4' or '8' or '5' or '9' or '6' or '-' or '+' or '1' or '2' or '3' or 'q' or '' or 'backspace') or (first == 1):
                if key == '7':
                    EL = (EL + 2)
                if key == str(4) and EL > 0:
                    EL = (EL - 2)
                if key == str(8):
                    IN = (IN + 2)
                if key == str(5) and IN > 0:
                    IN = (IN - 2)
                if key == str(9):
                    TF = (TF + 5)
                if key == str(6) and TF > 0:
                    TF = (TF - 5)
                if key == str('-') and iso_key < 7:
                    iso_key = iso_key + 1
                if key == str('+') and iso_key > 1:
                    iso_key = iso_key - 1
                if key == '':
                    if (dbase["Target"] != "Custom") and ((EL != dbase["EL"]) or (iso_key != dbase["iso_key"])):
                        lcd.clear()
                        lcd.text("CONFIRM UPDATE", 1)
                        lcd.text("TO EXPO SETTINGS?", 2)
                        lcd.text("1) YES    2) NO", 4)
                        #print(0.5)
                        flag = True
                        while flag:
                            key = readchar.readkey().strip()
                            if (key == "1") or (key == "2"):
                                flag = False
                        if key == "1":
                            break
                    else:
                        break
                if first == 1:
                    first = 0
                ISO = iso_index[iso_key]
                lcd.text(dbase["Target"] + "("+ str(percent) + "->" + str(round(((dbase["EC"] + (EL*TF/60)) / dbase["EG"]) * 100)) + "%)", 1)
                lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF), 2)
                lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                est_time = round(((EL+IN) * TF) / 60)
                est_expo = round((EL * TF) / 60)
                lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)
                print()
        updates = {"EL":EL, "IN":IN, "TF":TF, "iso_key":iso_key}
        dbase = {**dbase, **updates}
        #print(dbase)
        return dbase


    #except Exception as e:
        #lcd.clear()
        #lcd.text("ERROR OCCURRED", 1)
