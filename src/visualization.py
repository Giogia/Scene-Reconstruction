import numpy as np
import matplotlib.pyplot as plt


def show_array(data):
    data /= np.max(data)
    plt.imshow(data, interpolation='bicubic')
    plt.show()
