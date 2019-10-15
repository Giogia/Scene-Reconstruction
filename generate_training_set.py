import csv
import os
from math import cos, sin, pi, radians
from random import random

from bpy import context, data, ops
from mathutils import Vector

# CONFIGURATION PARAMETERS
PATH = '/Users/giovanni/Developer/blender-scene'

SAMPLES = 100

DISTANCE: float = 5  # meters
DISTANCE_NOISE: float = 1

PITCH_NOISE: float = 10  # degrees

FOV: float = 65  # degrees
FOV_NOISE: float = 10

# RENDERING SETTINGS
OUTPUT_RESOLUTION = 100


def main():

    # Explore directory and run for every model in models
    for directory in os.listdir(os.path.join(PATH, 'models')):
        if os.path.isdir(os.path.join(PATH, 'models', directory)):

            for file in os.listdir(os.path.join(PATH, 'models', directory)):
                if file.endswith('.fbx'):

                    clean_cameras()

                    name = os.path.splitext(file)[0]
                    print('\n\n\nTraining samples from the following model:', name)

                    model = data.objects[name]
                    camera = create_camera()

                    move_camera(camera, model)

                    render(model, camera)


def clean_cameras():

    for item in data.objects:
        if 'training-camera' in item.name:
            data.objects.remove(item)


def create_camera():

    ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0))

    camera = context.active_object
    camera.name = 'training-camera'

    return camera


def node_setup():

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


def noise(value):
    return value * (random() - 0.5)


def move_camera(camera, model):

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


def render(model, camera):

    node_setup()

    # Rendering options
    context.scene.render.use_overwrite = True
    context.scene.render.use_placeholder = True
    context.scene.render.use_file_extension = True
    context.scene.render.resolution_percentage = OUTPUT_RESOLUTION

    context.scene.render.image_settings.file_format = 'OPEN_EXR'
    context.scene.render.image_settings.use_zbuffer = True
    context.scene.render.image_settings.use_preview = False

    for i in range(SAMPLES):
        move_camera(camera, model)

        context.scene.render.filepath = os.path.join(PATH, 'training', model.name, 'training_' + str(i))
        context.scene.camera = camera
        ops.render.render(animation=False, write_still=True)

    print('Rendering completed Successfully')


def save_cameras(model, camera):

    file = os.path.join(PATH, 'training', model.name, 'cameras.csv')
    writer = csv.writer(open(file, 'w'))

    header = ['Name', 'Location', 'Quaternion', 'Fov']
    writer.writerow(header)

    for i in range(SAMPLES):
        position = [coordinate for coordinate in camera.location]
        rotation = [direction for direction in camera.rotation_quaternion]
        writer.writerow([camera.name, position, rotation, FOV])

    print('File written Successfully')


main()


