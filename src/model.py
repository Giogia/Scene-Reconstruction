import open3d as o3d
import os
from math import cos, sin, radians, tan
from parameters import *
from exr import *
from load_save import read_csv
import trimesh

FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)


def generate_point_cloud(image, depth):

    model = []
    colors = []

    height = image.shape[0]
    width = image.shape[1]

    center_x = width/2
    center_y = height/width/2

    # remove the background from points
    for row in range(height):
        for column in range(width):

            distance = depth[row][column]

            if distance < 10:

                color = image[row][column]
                focal_length = 1 / (2 * tan(radians(FOV) / 2))

                y = distance * (column - center_x) / width / focal_length  # blender y
                z = distance * ((height-row-1)/width - center_y) / focal_length  # blender z
                x = distance  # blender x

                model.append([x, y, z])  # +z in blender
                colors.append(color)

    assert len(model) == len(colors)

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(model)
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    return point_cloud


def transform_model(point_cloud, location=(0, 0, 0), rotation=(0, 0, 0)):

    x = -location[0]
    y = location[1]
    z = location[2]

    angle_x = radians(-rotation[1])
    angle_y = radians(rotation[0] - 90)
    angle_z = radians(rotation[2] - 90)

    rotation_matrix_x = [[1.0, 0.0, 0.0, 0.0],
                         [0.0, cos(angle_x), -sin(angle_x),  0.0],
                         [0.0, sin(angle_x), cos(angle_x), 0.0],
                         [0.0, 0.0, 0.0, 1.0]]

    rotation_matrix_y = [[cos(angle_y), 0.0, -sin(angle_y), 0.0],
                         [0.0, 1.0, 0.0, 0.0],
                         [sin(angle_y), 0.0, cos(angle_y), 0.0],
                         [0.0, 0.0, 0.0, 1.0]]

    rotation_matrix_z = [[cos(angle_z), sin(angle_z), 0.0, 0.0],
                         [-sin(angle_z), cos(angle_z), 0.0, 0.0],
                         [0.0, 0.0, 1.0, 0.0],
                         [0.0, 0.0, 0.0, 1.0]]

    if rotation != (0, 0, 0):
        point_cloud.transform(rotation_matrix_y)
        point_cloud.transform(rotation_matrix_x)
        point_cloud.transform(rotation_matrix_z)

    if location != (0, 0, 0):
        point_cloud.translate(np.asarray((x, y, z)))

    return point_cloud


def generate_model(name):

    final_model = []
    final_colors = []

    for i in range(CAMERAS):

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

            file = os.path.join('test', name, 'cameras.csv')

            location = read_csv(file=file, field='Location', row_number=i)
            rotation = read_csv(file=file, field='Rotation', row_number=i)

            point_cloud = transform_model(point_cloud, location=location, rotation=rotation)

            o3d.io.write_point_cloud(intermediate_model_path, point_cloud)

        # o3d.visualization.draw_geometries([point_cloud])

        final_model.append(np.asarray(point_cloud.points))
        final_colors.append(np.asarray(point_cloud.colors))

    final_point_cloud = o3d.geometry.PointCloud()
    final_point_cloud.points = o3d.utility.Vector3dVector(np.concatenate(final_model, axis=0))
    final_point_cloud.colors = o3d.utility.Vector3dVector(np.concatenate(final_colors, axis=0))

    output_path = os.path.join('test', name, 'model.ply')

    o3d.io.write_point_cloud(output_path, final_point_cloud)

    print('\r', 'Model Generation Complete', end=' ')

    return final_point_cloud


pcd = generate_model('Fox')
pcd.estimate_normals()
radii = [1, 2]
rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
print('bella')
o3d.visualization.draw_geometries([pcd, rec_mesh])
