import gps
import json
import time
import flask
import gevent
import sense_hat
import threading
import flask_sockets

class Gps(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps.gps(mode=gps.WATCH_ENABLE)
        self.running = True

    def run(self):
        while self.running:
            self.gpsd.next()

    def getGps(self):
        return self.gpsd

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)

gpsUnit = Gps()
gpsUnit.start()

sense = sense_hat.SenseHat()
sense.set_rotation(180)

@app.route("/")
def index():
    return flask.render_template('index.html',)

@sockets.route('/data')
def echo_socket(ws):
    while not ws.closed:
        timeout = gevent.Timeout(0.1)
        timeout.start()
        try:
            message = ws.receive()
            print message
        except gevent.Timeout:
            pass
        except:
            e = sys.exc_info()[0]
            app.logger.error('Connection failed: %s' % (e))
        finally:
            timeout.cancel()
        
        acceleration = sense.get_accelerometer_raw()
        ws.send(json.dumps({
            'time': gpsUnit.getGps().utc,
            'timestamp': gpsUnit.getGps().fix.time,

            'latitude': gpsUnit.getGps().fix.latitude,
            'longitude': gpsUnit.getGps().fix.longitude,
            'altitude': gpsUnit.getGps().fix.altitude,

            'mode': gpsUnit.getGps().fix.mode,

            'temperature': sense.get_temperature(),

            'acceleration_x': acceleration['x'],
            'acceleration_y': acceleration['y'],
            'acceleration_z': acceleration['z']
        }))

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

