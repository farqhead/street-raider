import streetraider

import json
import time
import flask
import gevent
import sense_hat
import threading
import flask_sockets

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)

gpsUnit = streetraider.getDefaultGps()

sense = sense_hat.SenseHat()
sense.set_rotation(180)

@app.route("/")
def index():
    return flask.render_template('index.html')

@sockets.route('/data')
def echo_socket(ws):
    while not ws.closed:
        timeout = gevent.Timeout(0.01)
        timeout.start()
        try:
            message = ws.receive()
        except gevent.Timeout:
            pass
        except:
            e = sys.exc_info()[0]
            app.logger.error('Connection failed: %s' % (e))
        finally:
            timeout.cancel()

        acceleration = sense.get_accelerometer_raw()
        ws.send(json.dumps({
            'time': str(gpsUnit.getGpsReport().utc),
            'timestamp': str(gpsUnit.getGpsReport().time),

            'latitude': gpsUnit.getGpsReport().lat,
            'longitude': gpsUnit.getGpsReport().lon,
            'altitude': gpsUnit.getGpsReport().alt,

            'mode': gpsUnit.getGpsReport().mode,

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

