
import time
import logging
import threading


class BackgroundTimer(threading.Thread):

    def __init__(self, handler, time_seconds = 60):

        self.time = time_seconds
        self.handler = handler
        super(BackgroundTimer, self).__init__(
            target = self.routine,
            daemon = True
        )

    def routine(self):
        print("cheking time")
        self.handler() # run the function
        time.sleep(self.time) # sleep for 60 seconds 
        self.routine()

