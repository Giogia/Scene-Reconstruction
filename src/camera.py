from math import radians, degrees
from mathutils import Vector
from bpy import context, ops, data
import numpy as np

from . import matrix_utils, parameters

from importlib import reload

reload(matrix_utils)
reload(parameters)


class Camera:

    def __init__(self):

        try:
            self.camera = context.scene.objects['Camera']
            print("Camera found in current scene\n")

        except KeyError:
            self.camera = self.create_camera(name='Camera', location=(0, 0, 0))

    def create_camera(self, name, location):
        ops.object.camera_add(enter_editmode=False, align='VIEW', location=location)
        camera = context.active_object
        camera.name = name
        camera.data.angle = radians(parameters.FOV)
        camera.data.clip_start = parameters.NEAR_PLANE
        camera.data.clip_end = parameters.FAR_PLANE

        return camera

    def move_to(self, position, target=None):
        self.camera.location = position
        if target:
            self.look_at_model(target)

    def look_at_model(self, target):
        self.camera.rotation_mode = 'QUATERNION'
        looking_direction = Vector(self.camera.location) - Vector(target.location)
        self.camera.rotation_quaternion = looking_direction.to_track_quat('Z', 'Y')
        self.camera.rotation_mode = 'XYZ'

    def get_intrinsics_matrix(self):
        camera = data.cameras['Camera']  # Camera corresponding to Test_Camera or Training_Camera

        scene = context.scene

        scale = scene.render.resolution_percentage / 100

        resolution_x = scene.render.resolution_x * scale
        resolution_y = scene.render.resolution_y * scale

        focal_length = camera.lens

        sensor_width = camera.sensor_width
        sensor_height = camera.sensor_height

        aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        alpha_u = focal_length * resolution_x / sensor_width
        alpha_v = focal_length * resolution_y / sensor_height * aspect_ratio

        u_0 = resolution_x / 2
        v_0 = resolution_y / 2

        matrix = [alpha_u, 0, u_0,
                  0, alpha_v, v_0,
                  0, 0, 1]

        return np.reshape(matrix, (3, 3))

    def get_pose_matrix(self):
        position = self.camera.location
        rotation = self.camera.rotation_euler

        position = [position[1], - position[2], - position[0]]
        rotation = [degrees(rotation[0]) - 90, - degrees(rotation[2]) + 90, - degrees(rotation[1])]

        # print('Position', position)
        # print('Rotation', rotation)

        matrix = np.matmul(matrix_utils.translate_matrix(position), matrix_utils.rotate_matrix(rotation, order='YXZ'))

        # return np.reshape(matrix, (4,4))

        return self.camera.matrix_world
