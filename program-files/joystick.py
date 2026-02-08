import serial
from serial.tools import list_ports
import time
import shared_state
print("shared_state id:", id(shared_state))

class Joystick:

    def __init__(self, lcd, log, joystick_stop):
        # Initialize serial
        self.lcd = lcd
        self.log = log
        self.joystick_stop = joystick_stop

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

    def get_pos(self, clear_buffer=True):
        DEADLOW = 400
        DEADHIGH = 600
        if clear_buffer:
            self.clear_buffer()
        data = ""
        try:
            data = self.arduino.readline()
        except:
            self.connect()
        data = str(data)
        data = data.strip()
        if "x =" not in data or "y =" not in data or "button" not in data:
            return ["center", 1]
        list = data.split(":")
        try:
            button = list[1].strip()
            button = button.split("= ")
            button = button[1]
            button = button[:-5]
        except:
            return ["center", 1]
        list = list[0].split(",")
        try:
            x_list = list[0]
            x_list = x_list.strip()
            x_list = x_list.split("= ")
            x = int(x_list[1])
        except:
            return ["center", 1]
        try:
            y_list = list[1]
            y_list = y_list.strip()
            y_list = y_list.split("= ")
            y = int(y_list[1])
        except:
            return ["center", 1]
        print("x =", x, ", y =", y)
        if 400 < x < 600 and 400 < y < 600:
            pos = "center"
        elif x < 400:
            pos = "left"
        elif x > 600:
            pos = "right"
        elif y < 400:
            pos = "up"
        elif y > 600:
            pos = "down"
        else:
            pos = "center"
        return [pos, button]

    def run(self):
        while not self.joystick_stop.is_set():
            try:
                data = self.get_pos()
                shared_state.set_joystick_state(data[0], data[1])
                time.sleep(0.001)
            except Exception as e:
                print(e)
