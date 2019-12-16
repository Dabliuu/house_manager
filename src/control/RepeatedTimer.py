
import time
import logging
import threading

class RepeatedTimer(object):

    def __init__(self, interval, my_function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.my_function = my_function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = 0
        self.start()

    def _run(self):
        logging.debug("____run")
        if self.is_running:
            self.my_function(*self.args, **self.kwargs)
            self.next_call += self.interval
            #print(datetime.now().microsecond)
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def start(self):
        logging.debug("____start")
        if not self.is_running:
            self.next_call = self.interval + time.time()
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False