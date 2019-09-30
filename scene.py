from bpy import context, data, ops
from math import pi, sin, cos
import os

# CONFIGURATION PARAMETERS

PATH = '/Users/giovannitommasi/Repositories/blender-scene'
#PATH = './'
CAMERAS = 8
DISTANCE: float = 8
FOCAL_LENGTH: float = 45
RESOLUTION = 100


def main():

    for file in os.listdir(os.path.join(PATH, 'models')):
        if file.endswith('.fbx'):
            name = os.path.splitext(file)[0]

            clear_scene()
            add_lights()
            add_plane()
            model = add_model(name)

            setup_cameras(model)
            render(model)
            render(model, 'depth')


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

    ops.screen.frame_jump(end=False)


def add_lights():
    ops.object.light_add(type='SUN', radius=1, location=(DISTANCE/4, DISTANCE/8, DISTANCE/2))


def add_plane():
    ops.mesh.primitive_plane_add(size=DISTANCE, calc_uvs=True, enter_editmode=False, location=(0, 0, 0))


def add_model(name):
    path = os.path.join(PATH, 'models', name + '.fbx')
    ops.import_scene.fbx(filepath=path)
    model = context.active_object
    model.name = name

    return model


def setup_cameras(model):

    for i in range(CAMERAS):
        angle = i * pi / 4
        x = DISTANCE * cos(angle)
        y = DISTANCE * sin(angle)

        # Adding Camera
        ops.object.camera_add(enter_editmode=False, align='VIEW', location=(x, y, 1.0), rotation=(0.0, 0.0, 0.0))
        camera = context.active_object
        camera.name = 'camera' + str(i)
        camera.data.lens = FOCAL_LENGTH
        camera.data.shift_y = 0.2

        # Camera constraint to look at model
        ops.object.constraint_add(type='TRACK_TO')
        tracking = camera.constraints[0]
        tracking.target = data.objects[model.name]
        tracking.track_axis = 'TRACK_NEGATIVE_Z'
        tracking.up_axis = 'UP_Y'


def node_setup(mode):

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

    if mode == 'render':
        links.new(render_node.outputs['Image'], composite_node.inputs['Image'])

    elif mode == 'depth':
        normalize_node = tree.nodes.new('CompositorNodeNormalize')
        mix_node = tree.nodes.new('CompositorNodeMixRGB')

        links.new(render_node.outputs['Depth'], normalize_node.inputs['Value'])
        links.new(normalize_node.outputs['Value'], mix_node.inputs['Image'])
        links.new(render_node.outputs['Image'], mix_node.inputs['Fac'])
        links.new(mix_node.outputs['Image'], composite_node.inputs['Image'])

    else:
        raise Exception('Invalid Node Setup')


def render(model, mode='render'):

    # Rendering options
    context.scene.render.use_overwrite = True
    context.scene.render.use_placeholder = True
    context.scene.render.use_file_extension = True
    context.scene.render.resolution_percentage = RESOLUTION

    node_setup(mode)

    for i in range(CAMERAS):
        camera = data.objects['camera' + str(i)]
        context.scene.render.filepath = os.path.join(PATH, 'rendering', model.name, camera.name, mode + '_')
        context.scene.camera = camera

        ops.render.render(animation=False, write_still=True)

    print('Completed Successfully')


main()
