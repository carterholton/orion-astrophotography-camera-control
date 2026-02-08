import time
import sys
import os, signal, subprocess
import queue
from rpi_lcd import LCD
from gpiozero import LED
import shared_state
print("shared_state id:", id(shared_state))
lcd = LCD()

class Display:
    def __init__(self):
        print("Initializing LCD Tools")

    def update(self, dbase):
        menu = 0
        TF = dbase["TF"]
        IN = dbase["IN"]
        EL = dbase["EL"]
        TFi = TF
        ISO = iso[dbase["iso_key"]]
        lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TFi), 2)
        lcd.text("Av: " + str(Av) + " ISO:" + str(ISO), 3)
        if menu == 0:
            est_time = round(((EL + IN) * TFi) / 60)
            est_expo = round((EL * TFi) / 60)
            lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)

    def progress_bar(self, TF, TFi, Fnum, line=4):
        percent = ((str(round(100 * ((TFi - TF) / TFi)))) + "%")
        progress = (((TFi - TF) / TFi) * 14)
        shots_left = (TFi - Fnum)
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
        lcd.text(percent + "[" + bar_filled + bar_unfilled + "]", line)

    def status_bar(self, status, line=2):
        status_label = status_id[status]
        lcd.text("STATUS: " + status_label, line)

    def time_status_bar(self, mode, time_left, status_label):
        if mode == "LIGHTS":
            lcd.text(">ACTIVE:" + str(time_left) + " min left<", 1)
        if mode == "DARKS":
            lcd.text(">DARKS:" + str(time_left) + " min left<", 1)
        lcd.text("STATUS: " + status_label, 2)

    def static_menu(self, window, Fnum=1, TFi=1, EL=1):
        match window:
            case "start":
                lcd.clear()
                lcd.text(">SYSTEM READY<", 1)
                lcd.text("Press 'UP' to begin", 2)
                lcd.text("Press 'DWN' to reboot", 4)
            case "paused":
                lcd.clear()
                lcd.text("   SHOOTING PAUSED   ", 2)
                lcd.text("   >UP to resume<    ", 3)
            case "finished":
                lcd.clear()
                lcd.text("Captured " + str(Fnum) + " Photos!", 1)
                lcd.text("Total EXP: " + str(round((TFi * EL) / 60)) + "min", 2)
            case "options":
                lcd.clear()
                lcd.text("<<    OPTIONS:       ", 1)
                lcd.text("UP) Pause Shooting   ", 2)
                
    def boot_screen(self, speed=0.00001):
        line1 = "  __   __ .  _   _  "
        line2 = " |  | |   | | | | | "
        line3 = " |__| |   | |_| | | "
        end = -20
        for i in range(20):
            lcd.text(line1[:end], 1)
            lcd.text(line2[:end], 2)
            lcd.text(line3[:end], 3)
            end += 1
            time.sleep(speed)

class DynamicMenu():
    def __init__(self, menu_queue, menu_stop, menu_items, submenu_items):
        #self.joystick = joystick
        self.title = "Options"
        self.header = self.title
        self.menu_queue = menu_queue
        self.menu_stop = menu_stop
        self.menu_items = menu_items
        self.submenu_items = submenu_items
        self.parent_index = 0
        self.parent_size = len(menu_items)
        self.child_index = 0
        self.child_sizes = [len(self.submenu_items[0]), len(self.submenu_items[1]), len(self.submenu_items[2])]
        self.level = 0
        self.menu_queue = menu_queue

    def show_menu(self):
        lcd.clear()
        lcd.text(self.header + ":", 1)
        for i in range(len(self.menu_items)):
            if i == self.parent_index:
                lcd.text(">" + self.menu_items[i], (i + 2))
            else:
                lcd.text(" " + self.menu_items[i], (i + 2))
        return "none"

    def show_submenu(self):
        lcd.clear()
        lcd.text(self.header + ":", 1)
        for i in range(len(self.submenu_items[self.parent_index])):
            if i == self.child_index:
                lcd.text(">" + self.submenu_items[self.parent_index][i], (i + 2))
            else:
                lcd.text(" " + self.submenu_items[self.parent_index][i], (i + 2))
        return "none"

    def next_parent(self):
        self.parent_index = (self.parent_index + 1) % (self.parent_size + 1)
        #("parent:", self.parent_index)
        self.show_menu()
        return "none"

    def prev_parent(self):
        self.parent_index = (self.parent_index - 1) % (self.parent_size + 1)
        #print("parent:", self.parent_index)
        self.show_menu()
        return "none"

    def next_child(self):
        max_child = self.child_sizes[self.parent_index] + 1
        self.child_index = (self.child_index + 1) % max_child
        #print("child:", self.child_index)
        self.show_submenu()
        return "none"

    def prev_child(self):
        max_child = self.child_sizes[self.parent_index] + 1
        self.child_index = (self.child_index - 1) % max_child
        #print("child:", self.child_index)
        self.show_submenu()
        return "none"

    def forward(self):
        # If in main menu
        if self.level == 0:
            # If menu item has a submenu, enter it
            if self.child_sizes[self.parent_index] != 0:
                self.level = 1
                self.header = self.menu_items[self.parent_index]
                self.child_index = 0
                self.show_submenu()
                return "none"
            # If menu item has no submenu, select the item
            else:
                return "select"
            
    def back(self):
        # If in submenu
        state = "none"
        if self.level == 1:
            self.level = 0
            self.parent_index = 0
            self.child_index = 0
            self.header = self.title
            self.show_menu()
        if self.level == 0:
            state = "exit"
        return state


    def update_menu(self, pos):
        #print(self.level)
        state = "none"
        if pos[1] == '0':
            state = self.forward()
        elif pos[0] == "left":
            state = self.back()
        elif pos[0] == "up":
            if self.level == 0:
                self.prev_parent()
            if self.level == 1:
                self.prev_child()
        elif pos[0] == "down":
            if self.level == 0:
                self.next_parent()
            if self.level == 1:
                self.next_child()
        if state != 'none' and state != 'exit':
            state = self.select_item()
        return state

    def select_item(self):
        if self.level == 0:
            item =self.menu_items[self.parent_index]
        else:
            item =self.submenu_items[self.parent_index][self.child_index]
        return item

    def reset(self):
        self.parent_index = 0
        self.child_index = 0
        self.level = 0

    def open(self):
        self.show_menu()
        state = "none"
        while state == 'none':
            joystick = shared_state.get_joystick_state()
            pos = [joystick["pos"], joystick["button"]]
            while (pos == ['center', '1']) and (state == 'none'):
                joystick = shared_state.get_joystick_state()
                pos = [joystick["pos"], joystick["button"]]
                state = self.update_menu(pos)
                if self.menu_stop.is_set():
                    return
        shared_state.set_menu_state(state)
        return True

    def run(self):
        while not self.menu_stop.is_set():
            pos = ['center', '1']
            while not pos == ['left', '0']:
                #pos = self.joystick.get_pos()
                joystick = shared_state.get_joystick_state()
                pos = [joystick["pos"], joystick["button"]]
                if self.menu_stop.is_set():
                    return
            shared_state.set_menu_state("state")
            status = self.open()