import os
from importlib import reload
from math import pi, sin, cos
from random import random

from bpy import context, data

from . import parameters
from .loader import export_view, export_matrix, export_model_parameters, create_directory

reload(parameters)


def noise(value):
    return value * (random() - 0.5)


class Renderer:

    def __init__(self):
        self.scene = context.scene
        self.settings = context.scene.render

        # Rendering options
        self.settings.use_overwrite = True
        self.settings.use_placeholder = True
        self.settings.use_file_extension = True
        self.settings.resolution_percentage = parameters.OUTPUT_RESOLUTION
        self.scene.render.resolution_x = parameters.RESOLUTION_X
        self.scene.render.resolution_y = parameters.RESOLUTION_Y

        self.settings.image_settings.file_format = 'OPEN_EXR'
        self.settings.image_settings.use_zbuffer = True
        self.settings.image_settings.use_preview = False

        self.scene.frame_start = parameters.START_FRAME
        self.scene.frame_end = parameters.END_FRAME
        self.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)

        # Switch on nodes
        self.scene.use_nodes = True
        tree = self.scene.node_tree
        links = tree.links

        # Clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)

        # Basic Node configuration
        render_node = tree.nodes.new('CompositorNodeRLayers')
        composite_node = tree.nodes.new('CompositorNodeComposite')

        links.new(render_node.outputs['Image'], composite_node.inputs['Image'])
        links.new(render_node.outputs['Depth'], composite_node.inputs['Z'])

    def render(self, camera, model, path, update_views=True):

        self.scene.camera = camera.camera

        # export intrinsic parameters
        intrinsic = camera.get_intrinsics_matrix()
        export_matrix(intrinsic, path, 'camera_intrinsic')

        export_model_parameters(model, path, 'model')

        samples = parameters.CAMERAS_NUMBER
        for i in range(samples):

            camera_name = 'camera_' + str(i + 1)

            create_directory(os.path.join(path, camera_name))

            # Generate semi random positions
            angle = 2 * pi * i / samples  # + noise(radians(parameters.YAW_NOISE))
            distance = parameters.DISTANCE  # + noise(parameters.DISTANCE_NOISE)
            height = model.location[2]  # + 2 * abs(noise(parameters.HEIGHT_NOISE))

            x = distance * cos(angle)
            y = distance * sin(angle)
            z = height

            camera.move_to((x, y, z), target=model)

            if update_views:
                # export background
                model.hide_render = True
                if parameters.EXTENSION == 'fbx':
                    data.objects['Mesh'].hide_render = True
                export_view(os.path.join(path, camera_name, 'background'))
                model.hide_render = False
                if parameters.EXTENSION == 'fbx':
                    data.objects['Mesh'].hide_render = False

                # export camera views
                for frame in range(self.scene.frame_start, self.scene.frame_end + 1):
                    self.scene.frame_set(frame)
                    export_view(os.path.join(path, camera_name, str(frame)))

            # export camera pose
            pose_matrix = camera.get_pose_matrix()
            export_matrix(pose_matrix, os.path.join(path, camera_name), 'pose')

        print('View extraction completed Successfully\n\n')
