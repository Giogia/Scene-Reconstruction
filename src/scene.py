from bpy import context, ops, data

from .parameters import *
from .loader import create_directory, import_model, save_model


def setup_scene(name):
    print('\n\nSetup the scene for the following model:' + name)
    create_directory(name)

    try:
        model = context.scene.objects[name]
        print('Found model in current scene')

    except KeyError:

        clear_scene()
        add_lights()
        add_plane()
        model = add_model(name)

    save_model(model)

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
    ops.mesh.primitive_circle_add(vertices=128, radius=5 * DISTANCE, fill_type='NGON', location=(0, 0, 0))


def add_model(name):
    import_model(name)
    model = context.active_object
    model.name = name
    ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

    context.view_layer.objects.active = model.children[0]
    increase_resolution(model)

    return model


def increase_resolution(model):
    while len(model.children[0].data.vertices) < POLY_NUMBER:
        ops.object.modifier_add(type='MULTIRES')
        ops.object.multires_subdivide(modifier='Multires')
        ops.object.modifier_apply(apply_as='DATA', modifier='Multires')
