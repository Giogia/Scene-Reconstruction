import os
from pathlib import Path
from bpy import context, data, ops

# CONFIGURATION PARAMETERS
PATH = os.path.abspath(Path(context.scene.sw_settings.filepath).parents[1])
DISTANCE: float = 5


def setup_scene(name):

    print('\n\nSetup the scene for the following model:' + name + '\n\n')

    clear_scene()
    add_lights()
    add_plane()
    model = add_model(name)

    directory_setup(model)

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


def add_plane():
    ops.mesh.primitive_circle_add(vertices=128, radius=DISTANCE, fill_type='NGON', location=(0, 0, 0))


def add_model(name):

    path = os.path.join(PATH, 'models', name, name + '.fbx')
    ops.import_scene.fbx(filepath=path)
    model = context.active_object
    model.name = name
    ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

    return model


def directory_setup(model):

    training_directory = os.path.join(PATH, 'training', model.name)

    if not os.path.exists(training_directory):
        os.makedirs(training_directory)

    test_directory = os.path.join(PATH, 'test', model.name)

    if not os.path.exists(test_directory):
        os.makedirs(test_directory)

