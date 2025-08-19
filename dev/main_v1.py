import time
import os, signal, subprocess
import keyboard
from rpi_lcd import LCD
lcd = LCD()

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

def killgphoto2Process():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if b'gvfsd-gphoto2' in line:
			pid = int(line.split(None,1) [0])
			os.kill(pid, signal.SIGKILL)
			
def Scanner():
    try:
        global TF
        global IN
        global EL
        global TFi
        global iso
        global iso_key
        global Av
        TF = 5
        IN = 5
        EL = 10
        Av = "NA"
        iso_key = 2
        TFi = TF
        global lcd
        global sense
        global kill1
        global kill2
        global kill3
        global menu
        global pause
        lcd.clear()
        #lcd.text("**Shooting PAUSED**",4)
        #lcd.text("       ORION       ",4)
        lcd.text("       ORION        ",1)
        lcd.text("   CAMERA CONTROL   ",2)
        lcd.text("   ENTER to start   ",4)
        ready = False
        while not ready:
            if keyboard.read_key() == 'enter':
                ready = True
        lcd.clear()
        lcd.text("Booting...",2)
        time.sleep(2)
        lcd.clear()
        lcd_update()
        Flag = False
        while not Flag:
            #print("Scanner launched")
            if keyboard.read_key() == '7' or '4' or '8' or '5' or '9' or '6' or '-' or '+' or '1' or '2' or '3' or 'q' or 'enter' or 'backspace':
                key = keyboard.read_key()
                if key == str(7):
                    EL = (EL + 2)
                    lcd_update()
                if key == str(4) and EL > 0:
                    EL = (EL - 2)
                    lcd_update()
                if key == str(8):
                    IN = (IN + 2)
                    lcd_update()
                if key == str(5) and IN > 0:
                    IN = (IN - 2)
                    lcd_update()
                if key == str(9):
                    TF = (TF + 5)
                    TFi = (TFi + 5)
                    lcd_update()
                if key == str(6) and TF > 0:
                    TF = (TF - 5)
                    TFi = (TFi - 5)
                    lcd_update()
                if key == str('-') and iso_key < 7:
                    iso_key = iso_key + 1
                    lcd_update()
                if key == str('+') and iso_key > 1:
                    iso_key = iso_key - 1
                    lcd_update()
                if key == 'enter':
                    shutter_control()
                    
    except Exception as e:
        lcd.clear()
        lcd.text("ERROR OCCURRED", 1)
        lcd.text("REBOOTING IN 5s", 2)
        time.sleep(5)
        Scanner()
                    
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
    menu = 0;
    #lcd.clear()
    ISO = iso[iso_key]
    lcd.text("EL:" + str(EL) + "s IN:" + str(IN) + "s TF:" + str(TFi), 2)
    lcd.text("Av: " + str(Av) + " ISO:" + str(ISO), 3)
    if menu == 0:
        est_time = round(((EL+IN) * TFi) / 60)
        est_expo = round((EL * TFi) / 60)
        lcd.text("[Timer:" + str(est_time) + "m Expo:" + str(est_expo) + "m]", 4)
    #pause()

def shutter_control():
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
    TFi = TF
    print("running 2")
    kill2 = 0
    #global darks
    pause = 0
    Fnum = 0
    alternate = 0
    darks = 0
    lcd.clear()
    ready = False;
    iso_text = 'iso=' + str(iso_key)
    subprocess.run(['gphoto2', '--set-config',  iso_text])
    lcd.text(">SYSTEM READY<", 1)
    lcd.text("Press 0 to begin", 2)
    lcd.text("Press '=' to reboot", 4)
    while not ready:
        if keyboard.read_key() == '0':
            ready = True
    while True:
        if kill2 == 0:
            if pause == 0:
                print("control triggered")
                #lcd.text("|" + str(TF) + "|")
                #sense.set_pixel(7, 0, (255, 0, 0))
                subprocess.run(['gphoto2', '--set-config', 'eosremoterelease=Immediate'])
                #print(TF)
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
                time.sleep(EL)
                """
                if keyboard.read_key() == '=':
                    main()
                    break
                """
                subprocess.run(['gphoto2', '--set-config', 'eosremoterelease="Release Full"'])
                #lcd.text(">ACTIVE:" + str(TF) + "(s) left<", 1)
                time_left = round((TF + (EL + (IN))) / 60)
                lcd.text(">ACTIVE:" + str(time_left) + " min left<", 1)
                #sense.set_pixel(7, 0, (0, 0, 0))
                time.sleep(IN)
                """
                if keyboard.read_key() == '=':
                    main()
                    break
                """
                if TF <= 0:
                    lcd.clear()
                    lcd.text("Captured " + str(Fnum) + " Photos!", 1)
                    lcd.text("Total EXP: " + str(round((TFi * EL) / 60)) + "min", 2)
                    if darks == 0:
                        lcd.text("Capture Dark Frames?", 3)
                        lcd.text("    4)Yes   5)No    ", 4)
                        while True:
                            if keyboard.read_key() == '4' or '5':
                                if keyboard.read_key() == '4':
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

def main():
    #try:
    killgphoto2Process()
    Scanner()
"""
except Exception as e:
        lcd.clear()
        lcd.text("ERROR OCCURRED", 1)
        lcd.text("REBOOTING IN 5s", 2)
        time.sleep(5)
        main()
""" 
main()


