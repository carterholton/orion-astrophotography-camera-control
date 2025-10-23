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
                lcd.text("Please Choose Option:", 1)
                lcd.text("Capture Darks", 2)
                while True:
                    pos = joystick.get_pos()
                    if pos[0] == 'up':
                        lcd.clear()
                        EL = dbase["EL"]
                        IN = dbase["IN"]
                        TF = self.total_darks
                        mode = "DARKS"
                        break
            if pos[0] == 'down':
                mode = "DONE"
                break
        print("exiting processing")
        return EL, IN, TF, mode