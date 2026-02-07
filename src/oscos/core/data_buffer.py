from collections import deque
from threading import Lock
import time

class TelemetryBuffer:
    def __init__(self, maxlen=100000):
        self.timestamps = deque(maxlen=maxlen)
        self.values = deque(maxlen=maxlen)
        self.lock = Lock()
        self._subscribers = []
        self._t0 = None

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def add(self, value, timestamp=None):
        with self.lock:
            if timestamp == None:
                if self._t0 is None:
                    self._t0 = time.time() 
                self.timestamps.append(time.time() - self._t0)
            else:
                if self._t0 is None:
                    self._t0 = timestamp
                self.timestamps.append(timestamp - self._t0)
            self.values.append(value)

        for cb in self._subscribers:
            cb(timestamp,value)

    def get_all(self):
        with self.lock:
            return list(self.timestamps), list(self.values)

    def get_latest(self, n):
        with self.lock:
            return list(self.timestamps)[-n:], list(self.values)[-n:]

    def clear(self):
        self.timestamps.clear()
        self.values.clear()
        self._t0 = None

class BufferRegistry:
    def __init__(self):
        self.raw_timestamps = TelemetryBuffer()
        self.speed = TelemetryBuffer()
        self.acceleration = TelemetryBuffer()
        self.rpm = TelemetryBuffer()
        
        self.speed_corrected = TelemetryBuffer()
        self.acceleration_corrected = TelemetryBuffer()

        self.speed_peaks = TelemetryBuffer()

buffer = BufferRegistry()
