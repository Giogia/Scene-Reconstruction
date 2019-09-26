from bpy import context, ops, data
from math import pi, sin, cos
import os

CAMERAS = 8
DISTANCE: float = 8
FOCAL_LENGTH: float = 45

PATH = '/Users/giovannitommasi/Repositories/blender-scene'

# Clear data from previous scenes
if data:
    for item in data.objects:
        item.user_clear()
        data.objects.remove(item)

    for item in data.meshes:
        item.user_clear()
        data.meshes.remove(item)

    for material in data.materials:
        material.user_clear()
        data.materials.remove(material)

    for texture in data.textures:
        texture.user_clear()
        data.textures.remove(texture)

# Setup Lights:
ops.object.light_add(type='SUN', radius=1, location=(DISTANCE/4, DISTANCE/8, DISTANCE/2))

# Add Plane:
ops.mesh.primitive_plane_add(size=DISTANCE, calc_uvs=True, enter_editmode=False, location=(0, 0, 0))

# Add Model
name = 'Fox'
path = os.path.join(PATH, 'models', name + '.fbx')
ops.import_scene.fbx(filepath=path)
model = context.object
model.name = name

# Setup Cameras

for i in range(CAMERAS):

    angle = i * pi / 4
    x = DISTANCE * cos(angle)
    y = DISTANCE * sin(angle)

    ops.object.camera_add(enter_editmode=False, align='VIEW', location=(x, y, 1.0), rotation=(0.0, 0.0, 0.0))
    camera = context.object
    camera.name = 'camera' + str(i)
    camera.data.lens = FOCAL_LENGTH
    camera.data.shift_y = 0.2

    ops.object.constraint_add(type='TRACK_TO')

    tracking = camera.constraints[0]
    tracking.target = data.objects[model.name]
    tracking.track_axis = 'TRACK_NEGATIVE_Z'
    tracking.up_axis = 'UP_Y'

    # Setup output path for rendering
    context.scene.render.filepath = os.path.join(PATH, 'rendering', camera.name, str(i))

    context.scene.camera = camera
    ops.render.render(animation=False, write_still=True)

