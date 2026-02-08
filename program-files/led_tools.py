import time

class Led():
    def __init__(self, led, stop_event):
        self.led = led
        self.stop_event = stop_event

    def status_light(self, status, EL):
        while not self.stop_event.is_set():
            self.led.on()
            if "0" in status:
                time.sleep(1)
                self.led.off()
                time.sleep(1)
            elif "1" in status:
                time.sleep(0.25)
                self.led.off()
                time.sleep(0.25)