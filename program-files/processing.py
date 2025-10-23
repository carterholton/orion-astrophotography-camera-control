import time
class Preprocess:
    def __init__(self):
        self.total_darks = 20

    def run(self, dbase, lcd, stick):
        joystick = stick
        lcd.clear()
        lcd.text("Start Preprocessing?", 3)
        lcd.text("   UP)Yes   DN)No   ", 4)
        while True:
            pos = joystick.get_pos()
            if pos[0] == 'up':
                lcd.clear()
                lcd.text("Choose An Option:", 1)
                lcd.text("UP) Capture Darks", 2)
                joystick.clear_buffer()
                time.sleep(1)
                while True:
                    pos = joystick.get_pos()
                    if pos[0] == 'up':
                        lcd.clear()
                        EL = dbase["EL"]
                        IN = dbase["IN"]
                        TF = self.total_darks
                        mode = "DARKS"
                        return EL, IN, TF, mode
            if pos[0] == 'down':
                mode = "DONE"
                break
        print("exiting processing")
        return EL, IN, TF, mode