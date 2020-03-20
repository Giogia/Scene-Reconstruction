from math import sin, cos, radians
import numpy as np


def identity():
    return np.array([[1, 0, 0, 0],
                       [0, 1, 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]], dtype=np.float)


def rotate_x_matrix(angle):
    matrix = identity()

    matrix[1][1] = matrix[2][2] = cos(radians(angle))
    matrix[1][2] = - sin(radians(angle))
    matrix[2][1] = sin(radians(angle))

    return matrix


def rotate_y_matrix(angle):
    matrix = identity()

    matrix[0][0] = matrix[2][2] = cos(radians(angle))
    matrix[0][2] = sin(radians(angle))
    matrix[2][0] = - sin(radians(angle))

    return matrix


def rotate_z_matrix(angle):
    matrix = identity()

    matrix[0][0] = matrix[1][1] = cos(radians(angle))
    matrix[0][1] = - sin(radians(angle))
    matrix[1][0] = sin(radians(angle))

    return matrix


def scale_matrix(scale):
    matrix = identity()

    matrix[0][0] = matrix[1][1] = matrix[2][2] = scale

    return matrix


def translate_matrix(position):
    matrix = identity()

    matrix[0][3] = position[0]
    matrix[1][3] = position[1]
    matrix[2][3] = position[2]

    return matrix


def rotate_matrix(rotation):
    matrix = np.matmul(rotate_x_matrix(rotation[0]), rotate_y_matrix(rotation[1]))

    return np.matmul(matrix, rotate_z_matrix(rotation[2]))
