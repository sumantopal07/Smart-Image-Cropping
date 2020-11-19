from app import app
from flask import request, redirect, url_for,send_file, send_from_directory, safe_join, abort,render_template

import os


@app.route("/")
def index():
    import eventlet
    import socketio

    sio = socketio.Server()
    x = socketio.WSGIApp(sio)

    @sio.event
    def connect(sid, environ):
        print('connect ', sid)

    @sio.event
    async def message(sid, data):
        print("message ", data, json.loads(data))
        # send a reply to the sender client socket 
        # await sio.emit('reply', room=sid)

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)
    return render_template("public/xyz.html")
    # # print(os.getcwd()+"/app/static/img/uploads")
    # # return redirect(url_for('upload_image'))
    # return render_template("public/xyz.html")


@app.route("/admin")
def admin():
    return redirect("https://github.com/sumantopal07/Content-Aware-Resizing-using-Dynamic-Programming",code=302)

from werkzeug.utils import secure_filename


app.config["IMAGE_UPLOADS"] = os.getcwd()+"/app/static/img/uploads/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@app.route("/upload_image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:

            if "filesize" in request.cookies:

                if not allowed_image_filesize(request.cookies["filesize"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)

                image = request.files["image"]

                if image.filename == "":
                    print("No filename")
                    return redirect(request.url)

                if allowed_image(image.filename):
                    filename = secure_filename(image.filename)

                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                    print("Image saved")
                    send_file(app.config["IMAGE_UPLOADS"]+filename,as_attachment=True)
                    return redirect(url_for('upload_image'))

                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("public/upload_image.html")