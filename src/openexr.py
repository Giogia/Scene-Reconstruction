from PIL import Image
from OpenEXR import InputFile
import Imath
import numpy as np
import pptk

PATH = 'test/Fox/camera0/render_.exr'
FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)


def exr_to_array(path):

    file = InputFile(path)
    window = file.header()['dataWindow']
    channels = ('R', 'G', 'B', 'A')

    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    channels_tuple = [np.frombuffer(channel, dtype=np.float32) for channel in file.channels(channels, FLOAT)]
    exr_array = np.dstack(channels_tuple)
    return exr_array.reshape(size + (len(channels_tuple),))


def exr_to_depth(path):

    file = InputFile(path)
    window = file.header()['dataWindow']
    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    exr_depth = file.channel('Z', FLOAT)
    exr_depth = np.frombuffer(exr_depth, dtype=np.float32)
    exr_depth = np.reshape(exr_depth, size)

    return exr_depth


def encode_to_srgb(image_array):
    a = 0.055
    return np.where(image_array <= 0.0031308,
                    image_array * 12.92,
                    (1 + a) * pow(image_array, 1 / 2.4) - a)


def exr_to_srgb(path):

    exr_array = exr_to_array(path)
    srgb_array = encode_to_srgb(exr_array) * 255

    return Image.fromarray(srgb_array.astype('uint8'), 'RGBA')


array = exr_to_array(PATH)
depth = exr_to_depth(PATH)
image = exr_to_srgb(PATH).convert('RGB')


model = []
colors = []
for i in range(depth.shape[0]):
    for j in range(depth.shape[1]):
        if depth[i][j] < 6:
            model.append([depth[i][j] / 5, (1920 - j) / 1920, (1080 - i) / 1920])
            colors.append(array[i][j])

viewer = pptk.viewer(model)
viewer.color_map(colors)
viewer.set(point_size=0.001)

