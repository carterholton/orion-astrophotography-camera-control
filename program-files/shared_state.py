import threading

# shared joystick state
_joystick_state = {
    "pos": "center",
    "button": 0
}

_menu_selection = ""

# Lock to protect access
_state_lock = threading.Lock()
_lcd_lock = threading.Lock()

def set_joystick_state(pos, button):
    with _state_lock:
        global _joystick_state
        _joystick_state["pos"] = pos
        _joystick_state["button"] = button

def get_joystick_state():
    with _state_lock:
        # return a copy so callers can't mutate the internal dict
        return dict(_joystick_state)

def set_menu_state(state):
    with _lcd_lock:
        global _menu_selection
        _menu_selection = state

def get_menu_state():
    with _lcd_lock:
        return _menu_selection
