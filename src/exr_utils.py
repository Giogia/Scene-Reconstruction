from Imath import PixelType
import numpy as np
from PIL import Image
from OpenEXR import InputFile


def exr_to_image(path):
    file = InputFile(path)
    window = file.header()['dataWindow']
    channels = ('R', 'G', 'B')

    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    channels_tuple = [np.frombuffer(channel, dtype=np.float32)
                      for channel in file.channels(channels, PixelType(PixelType.FLOAT))]
    exr_array = np.dstack(channels_tuple)
    return exr_array.reshape(size + (len(channels_tuple),))


def exr_to_depth(path, far_threshold=100000):
    file = InputFile(path)
    window = file.header()['dataWindow']
    size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

    exr_depth = file.channel('Z', PixelType(PixelType.FLOAT))
    exr_depth = np.fromstring(exr_depth, dtype=np.float32)
    exr_depth[exr_depth > far_threshold] = 0
    exr_depth = np.reshape(exr_depth, size)

    return exr_depth


def encode_to_srgb(image_array):
    a = 0.055
    return np.where(image_array <= 0.0031308,
                    image_array * 12.92,
                    (1 + a) * pow(image_array, 1 / 2.4) - a)


def exr_to_pil_image(path):
    exr_array = exr_to_image(path)
    srgb_array = encode_to_srgb(exr_array) * 255

    return Image.fromarray(srgb_array.astype('uint8'), 'RGB')