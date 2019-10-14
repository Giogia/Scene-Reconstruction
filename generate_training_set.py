from bpy import context, data, ops
from math import cos, sin, pi, radians
from mathutils import Vector
from random import random
import os


# CONFIGURATION PARAMETERS
PATH = '/Users/giovanni/Developer/blender-scene'

SAMPLES = 1000

DISTANCE: float = 5
DISTANCE_NOISE: float = 1

FOV: float = 65
FOV_NOISE: float = 10

HEIGHT_NOISE: float = 1

# RENDERING SETTINGS
OUTPUT_RESOLUTION = 10


def main():
    for directory in os.listdir(os.path.join(PATH, 'models')):
        if os.path.isdir(os.path.join(PATH, 'models', directory)):

            for file in os.listdir(os.path.join(PATH, 'models', directory)):
                if file.endswith('.fbx'):

                    name = os.path.splitext(file)[0]
                    print('\n\n\nTraining samples from the following model:', name)

                    model = data.objects[name]
                    camera = create_camera(model)

                    render(model, camera)


def noise(value):
    return value * (random() - 0.5)


def create_camera(model):

    angle = 2 * pi * random()

    x = DISTANCE * cos(angle) + noise(DISTANCE_NOISE)
    y = DISTANCE * sin(angle) + noise(DISTANCE_NOISE)
    z = model.location[2] + noise(HEIGHT_NOISE)

    # Adding Camera
    ops.object.camera_add(enter_editmode=False, align='VIEW', location=(x, y, z))

    camera = context.active_object
    camera.name = 'training-camera'

    return camera


def move_camera(camera, model):

    camera.data.angle = radians(FOV + noise(FOV_NOISE))  # 5 degrees noise

    angle = 2 * pi * random()

    x = DISTANCE * cos(angle) + noise(DISTANCE_NOISE)
    y = DISTANCE * sin(angle) + noise(DISTANCE_NOISE)
    z = model.location[2] + noise(HEIGHT_NOISE)

    camera.location = (x, y, z)

    camera.rotation_mode = 'QUATERNION'
    looking_direction = Vector(camera.location) - Vector(model.location)
    camera.rotation_quaternion = looking_direction.to_track_quat('Z', 'Y')


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


main()


