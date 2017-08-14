import gps
import copy
import time
import mutex
import threading

class Gps(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps.gps(mode=gps.WATCH_ENABLE)
        self.mutex = threading.Lock()
        self.running = True
        self.report = {}

    def run(self):
        while self.running:
            gpsReport = self.gpsd.next()
            timestamp = time.time()
            if gpsReport['class'] == 'DEVICE':
                self.gpsd.close()
                self.gpsd = gps.gps(mode=gps.WATCH_ENABLE)
            elif gpsReport['class'] == 'TPV':
                try:
                    self.mutex.acquire()
                    self.report = copy.deepcopy(gpsReport)
                    self.report['utc'] = self.report['time']
                    self.report['time'] = timestamp
                finally:
                    self.mutex.release()
            else:
                pass

    def getGpsReport(self):
        return self.report

def getDefaultGps():
    return default

default = Gps();
default.start();

