import os

from bpy import context, data
from pathlib import Path

from .parameters import *
from .camera import setup_camera, noise, move_camera
from .loader import save_camera_parameters, save_blender_image, save_camera_intrinsics
from .csv_utils import csv_setup

from math import pi, sin, cos, radians

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent


def setup_rendering_parameters():

    # Rendering options
    context.scene.render.use_overwrite = True
    context.scene.render.use_placeholder = True
    context.scene.render.use_file_extension = True
    context.scene.render.resolution_percentage = OUTPUT_RESOLUTION

    context.scene.frame_start = START_FRAME
    context.scene.frame_end = END_FRAME - 1

    context.scene.render.image_settings.file_format = 'OPEN_EXR'
    context.scene.render.image_settings.use_zbuffer = True
    context.scene.render.image_settings.use_preview = False

    # switch on nodes
    context.scene.use_nodes = True
    tree = context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # Basic Node configuration
    render_node = tree.nodes.new('CompositorNodeRLayers')
    composite_node = tree.nodes.new('CompositorNodeComposite')

    links.new(render_node.outputs['Image'], composite_node.inputs['Image'])
    links.new(render_node.outputs['Depth'], composite_node.inputs['Z'])


def render(model, samples, training=False):

    name = 'Training' if training else 'Test'

    camera_name = name+'_Camera'

    try:
        camera = context.scene.objects[camera_name]
        print("Found Camera in current scene")

    except KeyError:
        camera = setup_camera(name=camera_name, location=(0, 0, 0))

    camera_file = open(os.path.join(PATH, name, model.name, 'camera_calibration.csv'), 'w')
    save_camera_intrinsics(camera_file)

    frames_file = open(os.path.join(PATH, name, model.name, 'frames.csv'), 'w')
    writer = csv_setup(frames_file, CAMERA_FILE_HEADER)

    for i in range(samples):

        angle = 2 * pi * i / samples + noise(radians(YAW_NOISE))
        distance = DISTANCE + noise(DISTANCE_NOISE)
        height = HEIGHT + noise(HEIGHT_NOISE)

        x = distance * cos(angle)
        y = distance * sin(angle)
        z = height

        move_camera(camera, (x, y, z), model)

        file_path = os.path.join(PATH, name, model.name, str(i+1))
        save_blender_image(camera, file_path)
        save_camera_parameters(i+1, camera, writer, frames_file)

    print(name + ' set completed Successfully\n\n')
