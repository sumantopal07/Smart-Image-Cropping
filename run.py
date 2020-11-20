from flask import Flask, request, redirect, url_for, send_file, send_from_directory, safe_join, abort, render_template
from flask_socketio import SocketIO, send, emit
import os
import sys
import time
from tqdm import trange
import numpy as np
from imageio import imread, imwrite
from scipy.ndimage.filters import convolve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

############################################################################################################
############################################################################################################
############################################################################################################


def calc_energy(img):
    filter_du = np.array([
        [1.0, 2.0, 1.0],
        [0.0, 0.0, 0.0],
        [-1.0, -2.0, -1.0],
    ])
    # This converts it from a 2D filter to a 3D filter, replicating the same filter for each channel: R, G, B
    filter_du = np.stack([filter_du] * 3, axis=2)

    filter_dv = np.array([
        [1.0, 0.0, -1.0],
        [2.0, 0.0, -2.0],
        [1.0, 0.0, -1.0],
    ])
    filter_dv = np.stack([filter_dv] * 3, axis=2)

    img = img.astype('float32')
    convolved = np.absolute(convolve(img, filter_du)) + np.absolute(convolve(img, filter_dv))

    # Summing the energies in the red, green, and blue channels
    energy_map = convolved.sum(axis=2)

    return energy_map

def crop_c(img, scale_c):
    r, c, _ = img.shape
    new_c = int(scale_c * c)

    

    for i in range(c - new_c): # use range if you don't want to use tqdm. trange shows a progess bar on the terminal
        img = carve_column(img)

    return img

def crop_r(img, scale_r):
    img = np.rot90(img, 1, (0, 1))
    img = crop_c(img, scale_r)
    img = np.rot90(img, 3, (0, 1))
    return img

def carve_column(img):
    r, c, _ = img.shape

    M, backtrack = minimum_seam(img)

    # Create a (r, c) matrix filled with the value True
    mask = np.ones((r, c), dtype=np.bool)

    # Find the position of the smallest element in the last row of M
    j = np.argmin(M[-1])
    for i in reversed(range(r)):
        # Mark the pixels for deletion
        mask[i, j] = False
        j = backtrack[i, j]

    # Since the image has 3 channels, we convert our mask to 3D
    mask = np.stack([mask] * 3, axis=2)

    # Delete all the pixels marked False in the mask, and resize it to the new image dimensions
    img = img[mask].reshape((r, c - 1, 3))
    return img

def minimum_seam(img):
    r, c, _ = img.shape
    energy_map = calc_energy(img)

    M = energy_map.copy()
    backtrack = np.zeros_like(M, dtype=np.int)

    for i in range(1, r):
        for j in range(0, c):
            # Handle the left edge of the image, to ensure we don't index -1
            if j == 0:
                idx = np.argmin(M[i-1, j:j + 2])
                backtrack[i, j] = idx + j
                min_energy = M[i-1, idx + j]
            else:
                idx = np.argmin(M[i - 1, j - 1:j + 2])
                backtrack[i, j] = idx + j - 1
                min_energy = M[i - 1, idx + j - 1]

            M[i, j] += min_energy

    return M, backtrack

def MAIN(which_axis,scale,in_filename,out_filename):
    # if len(sys.argv) != 5:
    #     print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
    #     sys.exit(1)

    # which_axis = sys.argv[1]
    # scale = float(sys.argv[2])
    # in_filename = sys.argv[3]
    # out_filename = sys.argv[4]

    img = imread(in_filename)

    if which_axis == 'r':
        out = crop_r(img, scale)
    elif which_axis == 'c':
        out = crop_c(img, scale)
    else:
        print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
        sys.exit(1)
    
    imwrite(out_filename, out)

############################################################################################################
############################################################################################################
############################################################################################################


@socketio.on('my event')
def handle_message(message):
    print(message)
    for i in range(10000):
        emit("haha",i)





@app.route("/")
def index():
    return render_template("/public/upload_image.html")


@app.route("/admin")
def admin():
    return redirect("https://github.com/sumantopal07/Content-Aware-Resizing-using-Dynamic-Programming",code=302)

from werkzeug.utils import secure_filename


app.config["IMAGE_UPLOADS"] = os.getcwd()+"/static/img/uploads/"
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
                    render_template("/public/xyz.html")
                    MAIN()
                    return redirect(url_for('upload_image'))

                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("/public/upload_image.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app)
