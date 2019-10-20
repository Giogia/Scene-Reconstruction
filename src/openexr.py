from PIL import Image
from OpenEXR import InputFile
import Imath
import numpy as np
import open3d as o3d
from math import cos, sin, pi, log10

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


def display(image, depth):
    model = []
    colors = []

    # remove the background from points
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):

            if depth[i][j] < 100:
                model.append([j / 1920, (1080 - i) / 1920, - log10(depth[i][j]) ])
                colors.append(image[i][j])

    assert len(model) == len(colors)
    # Pass xyz to Open3D.o3d.geometry.PointCloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(model)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # o3d.io.write_point_cloud("prova.ply", pcd)
    # pcd = o3d.io.read_point_cloud("prova.ply")

    return pcd


final_model = []
final_colors = []

for i in range(8):

    PATH = 'test/Fox/camera' + str(i) + '/render_.exr'
    array = exr_to_array(PATH)
    depth = exr_to_depth(PATH)
    # image = exr_to_image(PATH)
    # image.show()

    pcd = display(array, depth)

    theta = i * 2 * pi / 8
    x = 0.5
    z = 1

    rotation_matrix = [[cos(theta), 0.0, sin(theta), 0.0],
                       [0.0, 1.0, 0.0, 0.0],
                       [-sin(theta), 0.0, cos(theta), 0.0],
                       [0.0, 0.0, 0.0, 1.0]]

    pcd.translate(np.asarray([-x, 0, z]))
    pcd.transform(rotation_matrix)

    o3d.io.write_point_cloud("prova"+str(i)+".ply", pcd)
    # pcd = o3d.io.read_point_cloud("prova"+str(i)+".ply")
    # o3d.visualization.draw_geometries([pcd])

    adding_points = np.asarray(pcd.points)
    final_model.append(np.asarray(pcd.points))
    final_colors.append(np.asarray(pcd.colors))

    print(i)

final_pcd = o3d.geometry.PointCloud()
final_pcd.points = o3d.utility.Vector3dVector(np.concatenate(final_model, axis=0))
final_pcd.colors = o3d.utility.Vector3dVector(np.concatenate(final_colors, axis=0))

o3d.visualization.draw_geometries([final_pcd])
