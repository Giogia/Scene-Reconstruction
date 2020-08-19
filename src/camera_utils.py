from importlib import reload
from math import radians

import numpy as np
from bpy import context, ops, data
from mathutils import Vector, Matrix

from . import matrix_utils, parameters

reload(matrix_utils)
reload(parameters)


class Camera:

    def __init__(self):

        try:
            self.camera = context.scene.objects['Camera']
            # print("Camera found in current scene\n")

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

    def rotate(self, rotation_matrix):

        matrix = Matrix(
            ((1, 0, 0),
             (0, -1, 0),
             (0, 0, -1)))

        rotation_matrix = np.array(matrix @ Matrix(rotation_matrix))
        rotation = Matrix(rotation_matrix[:3, :3]).to_quaternion()

        self.camera.rotation_mode = 'QUATERNION'
        self.camera.rotation_quaternion = rotation

    def get_intrinsics_matrix(self):
        camera = data.cameras['Camera']  # Camera corresponding to Test_Camera or Training_Camera

        scene = context.scene

        scale = scene.render.resolution_percentage / 100

        resolution_x = scene.render.resolution_x * scale
        resolution_y = scene.render.resolution_y * scale

        focal_length = camera.lens

        sensor_width = camera.sensor_width
        sensor_height = camera.sensor_height

        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        alpha_u = focal_length * resolution_x / sensor_width
        alpha_v = focal_length * resolution_y / sensor_height * pixel_aspect_ratio

        u_0 = resolution_x / 2
        v_0 = resolution_y / 2

        matrix = [alpha_u, 0, u_0,
                  0, alpha_v, v_0,
                  0, 0, 1]

        return np.reshape(matrix, (3, 3))

    def set_intrinsics_matrix(self, matrix):

        camera = data.cameras['Camera']  # Camera corresponding to Test_Camera or Training_Camera

        scene = context.scene

        scale = scene.render.resolution_percentage / 100

        alpha_u, alpha_v = matrix[0][0], matrix[1][1]
        u_0, v_0 = matrix[0][2], matrix[1][2]

        camera.sensor_width = alpha_v * u_0 / (alpha_u * v_0)
        camera.sensor_height = 1

        scene.render.resolution_x = 2 * u_0 / scale
        scene.render.resolution_y = 2 * v_0 / scale

        pixel_aspect_ratio = alpha_v/alpha_u

        scene.render.pixel_aspect_x = pixel_aspect_ratio * scene.render.pixel_aspect_y

        camera.lens = alpha_u * camera.sensor_width / (scene.render.resolution_x * scale)

        print(camera.lens)

    def get_pose_matrix(self):

        location = self.camera.location
        rotation = self.camera.rotation_quaternion

        rotation_matrix = rotation.to_matrix().transposed()
        location_matrix = -1 * rotation_matrix @ location

        matrix = Matrix(
            ((1, 0, 0),
             (0, -1, 0),
             (0, 0, -1)))

        location_matrix = matrix @ location_matrix
        rotation_matrix = matrix @ rotation_matrix

        matrix = Matrix((
            rotation_matrix[0][:] + (location_matrix[0],),
            rotation_matrix[1][:] + (location_matrix[1],),
            rotation_matrix[2][:] + (location_matrix[2],),
            (0, 0, 0, 1)
        ))

        return np.reshape(matrix, (4, 4))