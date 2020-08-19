import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from importlib import reload
from math import radians

from bpy import context, ops, data

from . import parameters

from .loader import create_directory, import_mesh, import_animation

reload(parameters)


# remove overloaded output when importing model
@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield err, out


class Scene:

    def __init__(self, path, name, file_name, reset=False):

        print('Setup model: ' + name + '\n')
        create_directory(path)
        self.animations = []

        if reset:
            self.clear_scene()
            self.add_lights()

        try:
            self.model = context.scene.objects[name]
        except KeyError:
            print('Added ' + name + ' model\n')
            self.add_model(name, file_name)

        for animation in parameters.ANIMATIONS:
            try:
                self.animations.append(context.scene.objects[animation])
            except KeyError:
                print('Added ' + animation + ' animation\n')
                self.add_animation(animation)

    def clear_scene(self):
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

    def add_lights(self):
        ops.object.light_add(type='SUN', radius=1,
                             location=(parameters.DISTANCE / 4, parameters.DISTANCE / 8, parameters.DISTANCE / 2))
        context.active_object.data.energy = 3.0

    def add_plane(self):
        ops.mesh.primitive_circle_add(vertices=128, radius=2 * parameters.DISTANCE, fill_type='NGON',
                                      location=(0, 0, 0))

    def add_model(self, name, file_name):

        with suppress_stdout_stderr():
            import_mesh(name, file_name)

        context.selected_objects[0].name = name
        '''
        context.view_layer.objects.active = data.objects[name]
        ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        '''

        self.model = data.objects[name]

    def add_animation(self, name):

        with suppress_stdout_stderr():
            import_animation(name)

        context.selected_objects[0].name = name

        self.animations.append(data.objects[name])