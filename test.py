import sys

# tqdm gives us a pretty progress bar to visualize progress.
from tqdm import trange
import numpy as np
from imageio import imread, imwrite
from scipy.ndimage.filters import convolve

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

    for i in trange(c - new_c): # use range if you don't want to use tqdm. trange shows a progess bar on the terminal
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

# def main():
#     if len(sys.argv) != 5:
#         print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
#         sys.exit(1)

#     which_axis = sys.argv[1]
#     scale = float(sys.argv[2])
#     in_filename = sys.argv[3]
#     out_filename = sys.argv[4]

#     img = imread(in_filename)

#     if which_axis == 'r':
#         out = crop_r(img, scale)
#     elif which_axis == 'c':
#         out = crop_c(img, scale)
#     else:
#         print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
#         sys.exit(1)
    
#     imwrite(out_filename, out)


def MAIN(which_axis,scale,in_filename,out_filename):
    # if len(sys.argv) != 5:
    #     print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
    #     sys.exit(1)

    # which_axis = sys.argv[1]
    # scale = float(sys.argv[2])
    # in_filename = sys.argv[3]
    # out_filename = sys.argv[4]

    # print(which_axis)
    # print(int(scale))
    # print(in_filename)
    # print(out_filename)
    # return 

    scale=float(scale)
    img = imread(in_filename)

    if which_axis == 'r':
        out = crop_r(img, scale)
    elif which_axis == 'c':
        out = crop_c(img, scale)
    else:
        print('usage: carver.py <r/c> <scale> <image_in> <image_out>', file=sys.stderr)
        sys.exit(1)
    
    imwrite(out_filename, out)
    
if __name__ == "__main__":
    a='r'
    b=0.75
    c='/home/sumanto/Desktop/PROJECT/Content-Aware-Resizing-using-Dynamic-Programming/static/img/uploads/Screenshot_from_2020-11-13_11-37-46.jpg'
    d='/home/sumanto/Desktop/PROJECT/Content-Aware-Resizing-using-Dynamic-Programming/static/img/downloads/new_image.jpg'
    MAIN(a,b,c,d)