import csv
import os
from math import pi, sin, cos, radians
from pathlib import Path
from random import random

from bpy import context, data, ops
from mathutils import Vector

# CONFIGURATION PARAMETERS
PATH = os.path.abspath(Path(context.scene.sw_settings.filepath).parents[1])
DISTANCE: float = 5

# CAMERAS SETTINGS
CAMERAS = 8
FOV: float = 65
NEAR_PLANE = 0.1
FAR_PLANE = 2 * DISTANCE

# RENDERING SETTINGS
OUTPUT_RESOLUTION = 100
START_FRAME = 0
END_FRAME = 250

SAMPLES = 100

DISTANCE_NOISE: float = 1  # meters
PITCH_NOISE: float = 10  # degrees
FOV_NOISE: float = 10  # degrees


def noise(value):
    return value * (random() - 0.5)


def create_training_camera():
    ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0))

    camera = context.active_object
    camera.name = 'training-camera'
    camera.data.clip_start = NEAR_PLANE
    camera.data.clip_end = FAR_PLANE

    return camera


def move_training_camera(camera, model):

    # set location
    horizontal_angle = 2 * pi * random()
    vertical_angle = noise(radians(PITCH_NOISE))
    distance = DISTANCE + noise(DISTANCE_NOISE)

    x = distance * cos(horizontal_angle) * cos(vertical_angle)
    y = distance * sin(horizontal_angle) * cos(vertical_angle)
    z = model.location[2] + distance * sin(vertical_angle)

    camera.location = (x, y, z)

    # set quaternion
    camera.rotation_mode = 'QUATERNION'
    looking_direction = Vector(camera.location) - Vector(model.location)

    camera.rotation_quaternion = looking_direction.to_track_quat('Z', 'Y')

    # set fov
    camera.data.angle = radians(FOV + noise(FOV_NOISE))


def setup_test_cameras(model):

    for i in range(CAMERAS):

        angle = 2 * pi * i / CAMERAS

        x = DISTANCE * cos(angle)
        y = DISTANCE * sin(angle)
        z = model.location[2]  # height of center of the model

        # Adding Camera
        ops.object.camera_add(enter_editmode=False, align='VIEW', location=(x, y, z))

        camera = context.active_object
        camera.name = 'camera' + str(i)
        camera.data.angle = radians(FOV)
        camera.data.clip_start = NEAR_PLANE
        camera.data.clip_end = FAR_PLANE

        # Make camera point at the center of the model
        camera.rotation_mode = 'QUATERNION'
        looking_direction = Vector(camera.location) - Vector(model.location)
        camera.rotation_quaternion = looking_direction.to_track_quat('Z', 'Y')


def render_setup():

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


def csv_setup(file):

    writer = csv.writer(file)

    header = ['Name', 'Location', 'Quaternion', 'Fov']
    writer.writerow(header)

    return writer


def save_image(camera, file_path):

    context.scene.render.filepath = file_path
    context.scene.camera = camera
    ops.render.render(animation=False, write_still=True)


def save_camera_parameters(name, camera, writer, file):

    position = [coordinate for coordinate in camera.location]
    rotation = [direction for direction in camera.rotation_quaternion]
    writer.writerow([name, position, rotation, FOV])
    file.flush()


def render_training(model):

    camera = create_training_camera()

    render_setup()
    file = open(os.path.join(PATH, 'training', model.name, 'cameras.csv'), 'w')
    writer = csv_setup(file)

    for i in range(SAMPLES):

        move_training_camera(camera, model)

        file_path = os.path.join(PATH, 'training', model.name, 'training_' + str(i))
        save_image(camera, file_path)
        save_camera_parameters(i, camera, writer, file)

    print('Training set completed Successfully\n\n')


def render_test(model):

    setup_test_cameras(model)

    '''name = 'Fox'
    data.objects.remove(data.objects['fox1'])  # TODO remove this
    for item in data.objects:
        print(item)'''

    render_setup()
    file = open(os.path.join(PATH, 'test', model.name, 'cameras.csv'), 'w')
    writer = csv_setup(file)

    for i in range(CAMERAS):

        camera = data.objects['camera' + str(i)]

        file_path = os.path.join(PATH, 'test', model.name, camera.name, 'render' + '_')
        save_image(camera, file_path)
        save_camera_parameters(camera.name, camera, writer, file)

    print('Test set completed Successfully\n\n')


