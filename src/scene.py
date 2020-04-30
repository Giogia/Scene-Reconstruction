from bpy import context, ops, data
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from importlib import reload
from . import loader, parameters

reload(loader)
reload(parameters)


# remove overloaded output when importing model
@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield err, out


class Scene:

    def __init__(self, name, reset=False):

        print('Setup the scene for the following model:' + name + '\n')
        loader.create_directory(name)

        try:
            self.model = context.scene.objects[name]
            print('Model found in current scene\n')

        except KeyError:
            reset = True

        if reset:
            self.clear_scene()
            self.add_lights()
            # self.add_plane()
            self.add_model(name)

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
        context.active_object.data.energy = 3.00

    def add_plane(self):
        ops.mesh.primitive_circle_add(vertices=128, radius=2 * parameters.DISTANCE, fill_type='NGON',
                                      location=(0, 0, 0))

    def add_model(self, name):

        with suppress_stdout_stderr():
            loader.import_mesh(name)

        self.model = data.objects[name]
        self.model.scale = [parameters.SCALE, parameters.SCALE, parameters.SCALE]
        self.set_model_resolution()

        context.view_layer.objects.active = self.model
        ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    def set_model_resolution(self):
        while len(self.model.data.vertices) < parameters.POLY_NUMBER:
            ops.object.modifier_add(type='MULTIRES')
            ops.object.multires_subdivide(modifier='Multires')
            ops.object.modifier_apply(apply_as='DATA', modifier='Multires')