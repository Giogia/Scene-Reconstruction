import os

from bpy import context, data
from pathlib import Path

from .loader import export_view, export_matrix

from math import pi, sin, cos, radians

from . import camera_utils, parameters
from importlib import reload

reload(camera_utils)
reload(parameters)

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def setup_rendering_parameters():

    # Rendering options
    context.scene.render.use_overwrite = True
    context.scene.render.use_placeholder = True
    context.scene.render.use_file_extension = True
    context.scene.render.resolution_percentage = parameters.OUTPUT_RESOLUTION

    context.scene.frame_start = parameters.START_FRAME
    context.scene.frame_end = parameters.END_FRAME - 1

    context.scene.render.image_settings.file_format = 'OPEN_EXR'
    context.scene.render.image_settings.use_zbuffer = True
    context.scene.render.image_settings.use_preview = False

    # Switch on nodes
    context.scene.use_nodes = True
    tree = context.scene.node_tree
    links = tree.links

    # Clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # Basic Node configuration
    render_node = tree.nodes.new('CompositorNodeRLayers')
    composite_node = tree.nodes.new('CompositorNodeComposite')

    links.new(render_node.outputs['Image'], composite_node.inputs['Image'])
    links.new(render_node.outputs['Depth'], composite_node.inputs['Z'])


def render(model, samples):

    path = os.path.join(PATH, 'data', model.name)

    try:
        camera = context.scene.objects['Camera']
        print("Camera found in current scene\n")

    except KeyError:
        camera = camera_utils.setup_camera(name='Camera', location=(0, 0, 0))

    camera_file = open(os.path.join(path, 'camera_intrinsics.csv'), 'w')
    intrinsics = camera_utils.get_intrinsics_matrix()
    export_matrix(intrinsics, camera_file)

    for i in range(samples):

        # Generate semi random positions
        angle = 2 * pi * i / samples + camera_utils.noise(radians(parameters.YAW_NOISE))
        distance = parameters.DISTANCE + camera_utils.noise(2 * parameters.DISTANCE_NOISE)
        height = abs(model.location[2] + camera_utils.noise(parameters.HEIGHT_NOISE))

        x = distance * cos(angle)
        y = distance * sin(angle)
        z = height

        camera_utils.move_camera(camera, (x, y, z), target=model)

        export_view(camera, os.path.join(path, str(i + 1)))

        frame_file = open(os.path.join(path, str(i+1) + '_pose.csv'), 'w')
        pose_matrix = camera_utils.get_pose_matrix(camera)
        export_matrix(pose_matrix, frame_file)

    print('View extraction completed Successfully\n\n')
