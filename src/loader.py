import os
from importlib import reload
from pathlib import Path

import numpy as np
from bpy import context, ops, data
from mathutils import Matrix

from . import parameters
from .csv_utils import csv_setup
from .matrix_utils import rotate_matrix, translate_matrix

reload(parameters)


# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def create_directory(path):

    if not os.path.exists(path):
        os.makedirs(path)


def import_mesh(name, file_name):
    model_path = os.path.join(PATH, 'models', name, file_name + '.' + parameters.EXTENSION)

    if parameters.EXTENSION == 'fbx':
        ops.import_scene.fbx(filepath=model_path, ignore_leaf_bones=False)

    if parameters.EXTENSION == 'obj':
        ops.import_scene.obj(filepath=model_path, axis_up='Z', axis_forward='Y')


def import_animation(name):
    animation_path = os.path.join(PATH, 'animations', name + '.bvh')
    ops.import_anim.bvh(filepath=animation_path)


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

    location = model.location
    rotation = model.rotation_quaternion

    rotation_matrix = rotation.to_matrix().transposed()
    location_matrix = -1 * rotation_matrix @ location

    matrix = Matrix(
        ((1, 0, 0),
         (0, -1, 0),
         (0, 0, -1)))

    location_matrix = matrix @ location_matrix
    rotation_matrix = matrix @ rotation_matrix

    matrix = Matrix((
        rotation_matrix[0][:] + (location_matrix[0],),
        rotation_matrix[1][:] + (location_matrix[1],),
        rotation_matrix[2][:] + (location_matrix[2],),
        (0, 0, 0, 1)
    ))

    export_matrix(matrix, path, name)


def export_view(file_path):
    context.scene.render.filepath = file_path
    ops.render.render(animation=False, write_still=True)


def export_matrix(matrix, path, name):

    file = open(os.path.join(path, name + '.csv'), 'w')
    writer = csv_setup(file)

    [writer.writerow(row) for row in matrix]
    file.flush()
