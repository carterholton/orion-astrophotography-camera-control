from rpi_lcd import LCD
lcd = LCD()
import time
import os

class Startup:

    def __init__(self, Display, dbase, log, joystick, camera):
        self.Display = Display
        self.dbase = dbase
        self.log = log
        self.joystick = joystick
        self.camera = camera
        self.iso_index = {
            0: 'AUTO',
            1: 100,
            2: 200,
            3: 400,
            4: 800,
            5: 1600,
            6: 3200,
            7: 6400,
            8: 12800}

    def system_check(self):
        lcd.clear()
        lcd.text("[....] Input check", 1)
        time.sleep(1)
        self.joystick.connect()
        lcd.text("[....] Camera check", 2)
        time.sleep(1)
        self.camera.connect(startup=True)
        lcd.text("", 3)
        lcd.text("", 4)
        lcd.text("ALL CHECKS PASSED!", 4)
        time.sleep(2)
        lcd.clear()

    def run(self):
        self.Display.boot_screen()
        time.sleep(1)
        lcd.text("Smart", 4)
        time.sleep(0.5)
        lcd.text("Smart Camera", 4)
        time.sleep(0.5)
        lcd.text("Smart Camera System ", 4)
        time.sleep(4)
        lcd.text("Waiting on input...", 4)
        alive = False
        while not alive:
            alive = self.joystick.scan()
            print(alive)
            time.sleep(5)
        self.log.info("Starting system checks")
        self.system_check()
        self.log.info("All system checks passed")
        lcd.text("      ORION CC      ", 1)
        lcd.text("UP) Load Project    ", 3)
        lcd.text("DN) Custom Shoot    ", 4)
        no_selection = True
        prev_pos = 'center'
        while no_selection:
            pos = self.joystick.get_pos()
            if pos[0] == 'up' and prev_pos[0] == 'center':
                self.load_project()
                no_selection = False
            elif pos[0] == 'down' and prev_pos[0] == 'center':
                update = {"Target": "Custom"}
                self.dbase = {**self.dbase, **update}
                self.cam_config()
                no_selection = False
            prev_pos = pos
        return self.dbase

    def load_project(self):
        lcd.clear()
        lcd.text("  Choose a project  ", 2)
        lcd.text("   From the list:   ", 3)
        time.sleep(2)
        lcd.clear()
        file_list = os.listdir("ProjectFiles")
        i = 0
        for file in file_list:
            if i <= 4:
                name = file.rsplit('.', 1)[0]
                # print(name)
                i += 1
                lcd.text(str(i) + ") " + name, i)
        no_selection = True
        prev_pos = 'center'
        while no_selection:
            pos = self.joystick.get_pos()
            if pos[0] == "up" and prev_pos[0] == "center":
                proj_index = 1
                no_selection = False
            elif pos[0] == 'down' and prev_pos[0] == 'center':
                proj_index = 2
                no_selection = False
            elif pos[0] == 'left' and prev_pos[0] == 'center':
                proj_index = 3
                no_selection = False
            elif pos[0] == 'right' and prev_pos[0] == 'center':
                proj_index = 4
                no_selection = False
            prev_pos = pos
        project = "ProjectFiles/" + file_list[proj_index - 1]
        with open(project, 'r') as file:
            lines = file.readlines()
            target = (lines[0].split(': ', 1)[1]).strip()
            EL = (lines[1].split(': ', 1)[1]).strip()
            IN = (lines[2].split(': ', 1)[1]).strip()
            TF = (lines[3].split(': ', 1)[1]).strip()
            iso_key = (lines[4].split(': ', 1)[1]).strip()
            expo_cap = (lines[5].split(': ', 1)[1]).strip()
            expo_goal = (lines[6].split(': ', 1)[1]).strip()

            self.dbase = {"Target": target, "EL": int(EL), "IN": int(IN), "TF": int(TF), "iso_key": int(iso_key),
                     "EC": float(expo_cap), "EG": float(expo_goal)}
            self.cam_config()

    def cam_config(self):
        #global dbase
        #global iso_index
        #global joystick
        lcd.clear()
        lcd.text("Booting...", 2)
        time.sleep(2)
        lcd.clear()
        EL = self.dbase["EL"]
        IN = self.dbase["IN"]
        TF = self.dbase["TF"]
        iso_key = self.dbase["iso_key"]
        # lcd.text("TARGET: " + dbase["Target"] + " (" + (str(round((dbase["EC"]/dbase["EG"])*100))) + "%)", 1)
        percent = (round((self.dbase["EC"] / self.dbase["EG"]) * 100))
        lcd.text(self.dbase["Target"] + "(" + str(percent) + "->" + str(
            round(((self.dbase["EC"] + (EL * TF / 60)) / self.dbase["EG"]) * 100)) + "%)", 1)
        # percent = (round((dbase["EC"]/dbase["EG"])*100))
        Flag = False
        first_run = True
        ISO = self.iso_index[iso_key]
        lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF), 2)
        lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
        est_time = round(((EL + IN) * TF) / 60)
        est_expo = round((EL * TF) / 60)
        lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)
        index = 0
        prev_pos = "center"
        while not Flag:
            pos = self.joystick.get_pos()
            # print(pos)
            list = ["ef", "in", "tf", "ios"]
            if pos[0] == "left" and prev_pos[0] == "center":
                if index == 0:
                    index = 3
                else:
                    index -= 1
            if pos[0] == "right" and prev_pos[0] == "center":
                if index == 3:
                    index = 0
                else:
                    index += 1
            if ((pos[0] == "right" or pos[0] == "left") and prev_pos[0] == "center") or first_run:
                if index == 0:
                    lcd.text(">EL:" + str(EL) + "s< IN:" + str(IN) + "s TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 1:
                    lcd.text("EL:" + str(EL) + "s >IN:" + str(IN) + "s< TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 2:
                    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s >TF:" + str(TF) + "<", 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 3:
                    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " >ISO:" + str(ISO) + "<", 3)
                first_run = False
            if (pos[0] == "up" or pos[0] == "down") and prev_pos[0] == "center":
                if index == 0:
                    if pos[0] == 'up':
                        EL = (EL + 2)
                    if pos[0] == 'down' and EL > 0:
                        EL = (EL - 2)
                if index == 1:
                    if pos[0] == 'up':
                        IN = (IN + 2)
                    if pos[0] == 'down' and IN > 0:
                        IN = (IN - 2)
                if index == 2:
                    if pos[0] == 'up':
                        TF = (TF + 5)
                    if pos[0] == 'down' and TF > 0:
                        TF = (TF - 5)
                if index == 3:
                    if pos[0] == 'up' and iso_key < 7:
                        iso_key = iso_key + 1
                    if pos[0] == 'down' and iso_key > 1:
                        iso_key = iso_key - 1
                ISO = self.iso_index[iso_key]
                lcd.text(self.dbase["Target"] + "(" + str(percent) + "->" + str(
                    round(((self.dbase["EC"] + (EL * TF / 60)) / self.dbase["EG"]) * 100)) + "%)", 1)
                print(self.dbase["Target"] + "(" + str(percent) + "->" + str(
                    round(((self.dbase["EC"] + (EL * TF / 60)) / self.dbase["EG"]) * 100)) + "%)")
                if index == 0:
                    lcd.text(">EL:" + str(EL) + "s< IN:" + str(IN) + "s TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 1:
                    lcd.text("EL:" + str(EL) + "s >IN:" + str(IN) + "s< TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 2:
                    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s >TF:" + str(TF) + "<", 2)
                    lcd.text("Av: " + "___" + " ISO:" + str(ISO), 3)
                if index == 3:
                    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF), 2)
                    lcd.text("Av: " + "___" + " >ISO:" + str(ISO) + "<", 3)
                print("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TF))
                print("Av: " + "___" + " ISO:" + str(ISO))
                est_time = round(((EL + IN) * TF) / 60)
                est_expo = round((EL * TF) / 60)
                lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)
                print("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]")
            prev_pos = pos
            if pos[1] == "0":
                if (self.dbase["Target"] != "Custom") and ((EL != self.dbase["EL"]) or (iso_key != self.dbase["iso_key"])):
                    lcd.clear()
                    lcd.text("CONFIRM UPDATE", 1)
                    lcd.text("TO EXPO SETTINGS?", 2)
                    lcd.text("UP) YES  DOWN) NO", 4)
                    time.sleep(0.1)
                    flag = True
                    while flag:
                        pos = self.joystick.get_pos()
                        if (pos[0] == "up") or (pos[0] == "down"):
                            flag = False
                    if pos[0] == "up":
                        break
                else:
                    break
        updates = {"EL": EL, "IN": IN, "TF": TF, "iso_key": iso_key}
        self.dbase = {**self.dbase, **updates}
        print("dbase updated", EL, IN, TF)