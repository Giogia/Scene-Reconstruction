from OpenEXR import InputFile
from Imath import PixelType
import numpy as np

file = InputFile('rendering/Cube/camera0/render_.exr')

window = file.header()['dataWindow']
size = (window.max.y - window.min.y + 1, window.max.x - window.min.x + 1)

depth = file.channel('Z', PixelType(PixelType.FLOAT))
depth = np.frombuffer(depth, dtype=np.float32)
depth = np.reshape(depth, size)

print(depth)