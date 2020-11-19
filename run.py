from app import app
import os
import eventlet
import socketio

sio = socketio.Server()
x = socketio.WSGIApp(sio)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    eventlet.wsgi.server(eventlet.listen(('', port)), x)
    print("sdfdsasdagadgadga")
    app.run(host='0.0.0.0', port=port)

# from seam_carving import *

# main('r',0.5,"img.jpg","new.jpg")sudo -H pip3 install python-socketio
