import os
from bpy import context
from math import pi, sin, cos, radians
from random import random

from .loader import export_view, export_matrix
from . import parameters
from importlib import reload

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

        self.settings.image_settings.file_format = 'OPEN_EXR'
        self.settings.image_settings.use_zbuffer = True
        self.settings.image_settings.use_preview = False

        self.scene.frame_start = parameters.START_FRAME
        self.scene.frame_end = parameters.END_FRAME - 1

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

    def render(self, camera, model, path):

        self.scene.camera = camera.camera

        # export intrinsic parameters
        intrinsic = camera.get_intrinsics_matrix()
        export_matrix(intrinsic, path, 'camera_intrinsics')

        samples = parameters.CAMERAS_NUMBER
        for i in range(samples):

            # Generate semi random positions
            angle = 2 * pi * i / samples + noise(radians(parameters.YAW_NOISE))
            distance = parameters.DISTANCE + noise(parameters.DISTANCE_NOISE)
            height = model.location[2] + 2 * abs(noise(parameters.HEIGHT_NOISE))

            x = distance * cos(angle)
            y = distance * sin(angle)
            z = height

            # export camera views
            camera.move_to((x, y, z), target=model)
            export_view(os.path.join(path, str(i + 1)))

            # export camera pose
            pose_matrix = camera.get_pose_matrix()
            export_matrix(pose_matrix, path, str(i+1) + '_pose')

        print('View extraction completed Successfully\n\n')