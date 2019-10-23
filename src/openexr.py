from PIL import Image
from OpenEXR import InputFile
import Imath
import numpy as np
import open3d as o3d
import os
from math import cos, sin, pi, pow, radians, tan
from parameters import *

FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)


def exr_to_array(path):
    file = InputFile(path)
    window = file.header()['dataWindow']
    channels = ('R', 'G', 'B')

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


def exr_to_image(path):
    exr_array = exr_to_array(path)
    srgb_array = encode_to_srgb(exr_array) * 255

    return Image.fromarray(srgb_array.astype('uint8'), 'RGB')


def generate_point_cloud(image, depth):

    model = []
    colors = []

    height = image.shape[0]
    width = image.shape[1]

    center_x = width/2
    center_y = height/2
    center_z = DISTANCE

    # remove the background from points
    for row in range(height):
        for column in range(width):

            distance = depth[row][column]

            if distance < 10:

                color = image[row][column]
                focal_length = 1 / (2 * tan(radians(FOV) / 2))

                x = distance * (column - center_x) / width / focal_length  # blender y
                y = distance * ((height-row-1) - center_y) / width / focal_length  # blender z
                z = distance - center_z  # blender x

                model.append([x, y, -z])  # +z in blender
                colors.append(color)

    assert len(model) == len(colors)

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(model)
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    # o3d.visualization.draw_geometries([point_cloud])

    return point_cloud


def transform_model(point_cloud, angle=0, x=0, y=0, z=0):

    # rotate on x axis
    rotation_matrix = [[cos(angle), 0.0, sin(angle), 0.0],
                       [0.0, 1.0, 0.0, 0.0],
                       [-sin(angle), 0.0, cos(angle), 0.0],
                       [0.0, 0.0, 0.0, 1.0]]

    point_cloud.translate(np.asarray([x, y, z]))
    point_cloud.transform(rotation_matrix)

    return point_cloud


def generate_model(name):

    final_model = []
    final_colors = []

    for i in range(1):

        print('\r', 'Analysing Models: ' + str(i+1) + '/' + str(CAMERAS), end=' ')

        rendering_path = os.path.join('test', name, 'camera' + str(i), 'render_.exr')

        intermediate_model_directory = os.path.join('test', name, 'intermediate_models')
        intermediate_model_path = os.path.join(intermediate_model_directory, str(i) + '.ply')

        if os.path.exists(intermediate_model_path):
            point_cloud = o3d.io.read_point_cloud(intermediate_model_path)

        else:
            if not os.path.exists(intermediate_model_directory):
                os.makedirs(intermediate_model_directory)

            array = exr_to_array(rendering_path)
            depth = exr_to_depth(rendering_path)
            point_cloud = generate_point_cloud(array, depth)

            theta = 2 * pi * i / CAMERAS

            point_cloud = transform_model(point_cloud, angle=theta)

            o3d.io.write_point_cloud(intermediate_model_path, point_cloud)

        final_model.append(np.asarray(point_cloud.points))
        final_colors.append(np.asarray(point_cloud.colors))

    final_point_cloud = o3d.geometry.PointCloud()
    final_point_cloud.points = o3d.utility.Vector3dVector(np.concatenate(final_model, axis=0))
    final_point_cloud.colors = o3d.utility.Vector3dVector(np.concatenate(final_colors, axis=0))

    output_path = os.path.join('test', name, 'model.ply')

    o3d.io.write_point_cloud(output_path, point_cloud)

    print('\r', 'Model Generation Complete', end=' ')

    return final_point_cloud


pcd = generate_model('Fox')
o3d.visualization.draw_geometries([pcd])
