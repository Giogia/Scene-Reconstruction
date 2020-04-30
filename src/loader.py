from math import degrees
from bpy import context, ops, data
import numpy as np
import os
from pathlib import Path

from .matrix_utils import scale_matrix, rotate_matrix, translate_matrix
from .parameters import MODEL_FILE_HEADER
from .csv_utils import csv_setup


# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def create_directory(name):

    data_directory = os.path.join(PATH, 'data', name)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)


def import_mesh(name, extension='obj'):
    model_path = os.path.join(PATH, 'models', name, name + '.' + extension)

    if extension == 'fbx':
        ops.import_scene.fbx(filepath=model_path)

    if extension == 'obj':
        ops.import_scene.obj(filepath=model_path, axis_up='Z', axis_forward='Y')


def export_mesh(model, extension='obj'):

    """ Save model parameters
    file = open(os.path.join(PATH, 'data', model.name, 'model.csv'), 'w')
    save_model_parameters(model, file)
    """

    # Generate Mesh
    context.view_layer.objects.active = model
    groundtruth_directory = os.path.join(PATH, 'data', model.name, 'groundtruth')

    if not os.path.exists(groundtruth_directory):
        os.makedirs(groundtruth_directory)

    filepath = os.path.join(groundtruth_directory, 'groundtruth.' + extension)

    if extension == 'glb':
        ops.export_scene.gltf(filepath=filepath , export_draco_mesh_compression_enable=True)

    elif extension == 'obj':
        ops.export_scene.obj(filepath=filepath)


def export_model_parameters(model, path, name):

    location_matrix = translate_matrix([coordinate for coordinate in model.location])
    rotation_matrix = rotate_matrix([degrees(angle) for angle in model.rotation_euler])

    matrix = np.matmul(location_matrix, rotation_matrix)

    export_matrix(matrix, path, name)


def export_view(file_path):
    context.scene.render.filepath = file_path
    ops.render.render(animation=False, write_still=True)


def export_matrix(matrix, path, name):

    file = open(os.path.join(path, name + '.csv'), 'w')
    writer = csv_setup(file)

    [writer.writerow(row) for row in matrix]
    file.flush()
