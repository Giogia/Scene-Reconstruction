from math import degrees
from bpy import context, ops, data
import numpy as np
import os
from pathlib import Path

from .matrix_utils import scale_matrix, rotate_matrix, translate_matrix
from . import parameters
from .csv_utils import csv_setup

from importlib import reload
reload(parameters)


# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def create_directory(path):

    if not os.path.exists(path):
        os.makedirs(path)


def import_mesh(name):
    model_path = os.path.join(PATH, 'models', name, name + '.' + parameters.EXTENSION)

    if parameters.EXTENSION == 'fbx':
        ops.import_scene.fbx(filepath=model_path)

    if parameters.EXTENSION == 'obj':
        ops.import_scene.obj(filepath=model_path, axis_up='Z', axis_forward='Y')


def export_mesh(model):

    """ Save model parameters
    file = open(os.path.join(PATH, 'data', model.name, 'model.csv'), 'w')
    save_model_parameters(model, file)
    """

    # Generate Mesh
    context.view_layer.objects.active = model
    groundtruth_directory = os.path.join(PATH, 'data', model.name, 'groundtruth')

    if not os.path.exists(groundtruth_directory):
        os.makedirs(groundtruth_directory)

    filepath = os.path.join(groundtruth_directory, 'groundtruth.' + parameters.EXTENSION)

    if parameters.EXTENSION == 'glb':
        ops.export_scene.gltf(filepath=filepath , export_draco_mesh_compression_enable=True)

    elif parameters.EXTENSION == 'obj':
        ops.export_scene.obj(filepath=filepath)


def export_model_parameters(model, path, name):

    position = model.location
    rotation = model.rotation_euler

    position = [position[0], position[2], position[1]]
    rotation = [rotation[0], rotation[2], rotation[1]]

    location_matrix = translate_matrix(position)
    rotation_matrix = rotate_matrix(rotation)

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
