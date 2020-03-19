import Imath
import numpy as np
from PIL import Image
from OpenEXR import InputFile


def exr_to_array(path):
    file = InputFile(path)
    window = file.header()['dataWindow']
    channels = ('R', 'G', 'B')

    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    channels_tuple = [np.frombuffer(channel, dtype=np.float32) for channel in file.channels(channels, Imath.PixelType(Imath.PixelType.FLOAT))]
    exr_array = np.dstack(channels_tuple)
    return exr_array.reshape(size + (len(channels_tuple),))


def exr_to_depth(path):
    file = InputFile(path)
    window = file.header()['dataWindow']
    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    exr_depth = file.channel('Z', Imath.PixelType(Imath.PixelType.FLOAT))
    exr_depth = np.frombuffer(exr_depth, dtype=np.float32)
    exr_depth = np.reshape(exr_depth, size)

    return exr_depth


def encode_to_srgb(image_array):
    a = 0.055
    return np.where(image_array <= 0.0031308,
                    image_array * 12.92,
                    (1 + a) * pow(image_array, 1 / 2.4) - a)


def exr_to_image(path):
    exr_array = exr_to_array(path)
    srgb_array = encode_to_srgb(exr_array) * 255

    return Image.fromarray(srgb_array.astype('uint8'), 'RGB')
