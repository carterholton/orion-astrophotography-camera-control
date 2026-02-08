import lcd_tools
import time
import logging
from rpi_lcd import LCD
from joystick import Joystick

log = logging.getLogger("log")
lcd = LCD()
joystick = Joystick(lcd, log)
joystick.connect()
menu = lcd_tools.DynamicMenu(joystick,
                             menu_items = ["Option 0", "Option 1", "Option 2"],
                             submenu_items = [["Sub0 Op0", "Sub0 Op1"], ["Sub1 Op0", "Sub1 Op1", "Sub1 Op2"], []]
)

selection = menu.open()
print(selection)


'''
state = menu.update_menu(["up", 1])
time.sleep(1)
state = menu.update_menu(["down", 0])
time.sleep(1)
state = menu.update_menu(["down", 1])
time.sleep(1)
state = menu.update_menu(["down", 1])
time.sleep(1)
'''