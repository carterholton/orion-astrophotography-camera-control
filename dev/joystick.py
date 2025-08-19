import serial
import time

class Joystick:

    def __init__(self):
        # Initialize serial
        print('Running. Press CTRL-C to exit.')
        self.arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        time.sleep(0.1) #wait for serial to open
        connected = False
        # Wait for Arduino to connect
        while not connected:
            if self.arduino.isOpen():
                print("{} connected!".format(self.arduino.port))
                connected = True

    def get_pos(self):
        data = self.arduino.readline()
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
        print(pos + " " + str(button))
