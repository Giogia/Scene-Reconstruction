import csv
import os
from bpy import context, ops, data
from . parameters import *
from pathlib import Path
from . load_save import save_model_parameters

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def setup_scene(name):

    print('\n\nSetup the scene for the following model:' + name + '\n\n')

    clear_scene()
    add_lights()
    add_plane()
    directory_setup(name)
    model = add_model(name)

    return model


def clear_scene():

    # Clear data from previous scenes
    if data:
        for item in data.objects:
            data.objects.remove(item)

        for item in data.meshes:
            data.meshes.remove(item)

        for material in data.materials:
            data.materials.remove(material)

        for texture in data.textures:
            data.textures.remove(texture)

    # Rewind Animation
    ops.screen.frame_jump(end=False)


def add_lights():
    ops.object.light_add(type='SUN', radius=1, location=(DISTANCE / 4, DISTANCE / 8, DISTANCE / 2))
    context.active_object.data.energy = 3.00


def add_plane():
    ops.mesh.primitive_circle_add(vertices=128, radius=DISTANCE, fill_type='NGON', location=(0, 0, 0))


def add_model(name):

    path = os.path.join(PATH, 'models', name, name + '.fbx')
    ops.import_scene.fbx(filepath=path)
    model = context.active_object
    model.name = name
    ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

    context.view_layer.objects.active = model.children[0]
    increase_resolution(model)
    save_model(model)
    
    file = open(os.path.join(PATH, 'test', model.name, 'model.csv'), 'w')
    save_model_parameters(file, model)

    return model


def increase_resolution(model):

    while len(model.children[0].data.vertices) < POLY_NUMBER:
        ops.object.modifier_add(type='MULTIRES')
        ops.object.multires_subdivide(modifier='Multires')
        ops.object.modifier_apply(apply_as='DATA', modifier='Multires')


def save_model(model):

    context.view_layer.objects.active = model.children[0]
    path = os.path.join(PATH, 'test', model.name, 'groundtruth.ply')
    ops.export_mesh.ply(filepath=path)


def directory_setup(name):

    training_directory = os.path.join(PATH, 'training', name)

    if not os.path.exists(training_directory):
        os.makedirs(training_directory)

    test_directory = os.path.join(PATH, 'test', name)

    if not os.path.exists(test_directory):
        os.makedirs(test_directory)
