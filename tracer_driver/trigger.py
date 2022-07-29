from time import time
from threading import Thread, Event

class triggerIO:
    def __init__(self):
        self.trigger_time=0
        self.onwait=False
        self.tcancel=Event
        self.tcancel.reset()
        self.trd=None
        self.pin=4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_trd(self, func):
        self.tcancel.reset()
        self.onwait=True
        self.trigger_time=0

        while GPIO.input(self.pin) == GPIO.HIGH:
            if self.tcancel.is_set():
                break
        
        self.onwait=False
        if not tcancel.is_set():
            self.trigger_time=time()
            func() # call the function

    def get_trigger_time(self):
        tt=0
        if self.trigger_time:
            tt=self.trigger_time
            self.trigger_time=0

        return tt

    def wait(self):
        self.trd=Thread(target=self.wait_trd)
        selg.start()

    def cancel(self):
        self.tcancel.reset()
        if self.trd:
            self.trd.join()
            self.trd=None


