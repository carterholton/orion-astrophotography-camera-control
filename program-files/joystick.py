import serial
from serial.tools import list_ports
import time

class Joystick:

    def __init__(self, lcd, log):
        # Initialize serial
        self.lcd = lcd
        self.log = log

    def scan(self):
        ports = list_ports.comports()
        alive = False
        for p in ports:
            print(p)
            if p != "":
                return True
        return False


    def connect(self):
        # Initialize serial
        self.lcd.clear()
        self.lcd.text("[....] Input check", 1)
        connected = False
        i = 12
        err_msg = ""
        while (connected == False) and (i > 0):
            try:
                self.arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
                time.sleep(0.1)  # wait for serial to open
                connected = False
                # Wait for Arduino to connect
                while not connected:
                    if self.arduino.isOpen():
                        print("{} connected!".format(self.arduino.port))
                        connected = True
                        break
            except Exception as e:
                err_msg = e
                self.lcd.text("[ERR!] Input check", 1)
                for j in range(10):
                    self.lcd.text(f"Retrying in {10 - j}s...", 4)
                    time.sleep(1)
                i -= 1
        if not connected:
            self.lcd.text("[FAIL] Input check", 1)
            self.lcd.text("FATAL ERROR OCCURRED", 4)
            time.sleep(1)
            self.log.error(err_msg, exc_info=True)
            exit()
        self.lcd.text("[PASS] Input check", 1)
        self.lcd.text("", 4)

    def clear_buffer(self):
        self.arduino.reset_input_buffer()

    def get_pos(self):
        data = ""
        try:
            data = self.arduino.readline()
        except:
            self.connect()
        data = str(data)
        data = data.strip()
        #print(data)
        list = data.split(":")
        x = 487
        y = 497
        button = 0
        pos = "center"
        try:
            button = list[1].strip()
            button = button.split("= ")
            button = button[1]
            button = button[:-5]
        except:
            i = 1
        list = list[0].split(",")
        try:
            x_list = list[0]
            x_list = x_list.strip()
            x_list = x_list.split("= ")
            x = int(x_list[1])
        except:
            i = 1
        try:
            y_list = list[1]
            y_list = y_list.strip()
            y_list = y_list.split("= ")
            y = int(y_list[1])
        except:
            i = 1
        if x < 400:
            pos = "left"
        if x > 550:
            pos = "right"
        if y < 400:
            pos = "up"
        if y > 550:
            pos = "down"
        return [pos, button]
        #print(pos + " " + str(button))
