import time
from threading import Timer as Timer


class CustomTimer:
    def __init__(self, duration, callback):
        self.duration = duration
        self.callback = callback
        self.start_time = time.time()
        self.pause_time = None

        self.timer = Timer(self.duration, self.callback)

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def pause(self):
        cur_time = time.time()
        self.pause_time = cur_time
        self.cancel()

    def resume(self):
        if self.pause_time:
            time_left = self.duration - (self.pause_time - self.start_time)
            self.duration = time_left
            self.start_time = time.time()

            self.timer = Timer(time_left, self.callback)
            self.start()
        else:
            self.timer = Timer(self.duration, self.callback)
            self.start()

    def get_time_left(self):
        time_left = self.duration - (self.pause_time - self.start_time) if self.pause_time else self.start_time
        return time_left * 1000  # in ms
