import matplotlib.pyplot as plt
import numpy as np


def show_array(data):
    data /= np.max(data)
    plt.imshow(data, interpolation='bicubic', cmap=plt.get_cmap('magma'))
    plt.show()
