from math import radians, degrees
from mathutils import Vector
from bpy import context, ops, data
from random import random
from .parameters import *
import numpy as np
from .matrix_utils import translate_matrix, rotate_matrix


def setup_camera(name, location):
    ops.object.camera_add(enter_editmode=False, align='VIEW', location=location)

    camera = context.active_object
    camera.name = name
    camera.data.angle = radians(FOV)
    camera.data.clip_start = NEAR_PLANE
    camera.data.clip_end = FAR_PLANE

    return camera


def move_camera(camera, position, model):
    camera.location = position
    look_at_model(camera, model)


def set_fov(camera, fov):
    camera.data.angle = radians(fov)


def look_at_model(camera, model):
    camera.rotation_mode = 'QUATERNION'
    looking_direction = Vector(camera.location) - Vector(model.location)
    camera.rotation_quaternion = looking_direction.to_track_quat('Z', 'Y')
    camera.rotation_mode = 'XYZ'


def noise(value):
    return value * (random() - 0.5)


def get_calibration_matrix():

    camera = data.cameras['Camera']  # Camera corresponding to Test_Camera or Training_Camera

    scene = context.scene

    scale = scene.render.resolution_percentage / 100
    resolution_x = scene.render.resolution_x * scale
    resolution_y = scene.render.resolution_y * scale

    focal_length = camera.lens

    sensor_width = camera.sensor_width
    sensor_height = camera.sensor_height

    aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    s_u = resolution_x / sensor_width
    s_v = resolution_y * aspect_ratio / sensor_height

    alpha_u = focal_length * s_u
    alpha_v = focal_length * s_v
    u_0 = resolution_x * scale / 2
    v_0 = resolution_y * scale / 2

    return [alpha_u, 0,       u_0,
            0,       alpha_v, v_0,
            0,       0,       1]


def get_pose_matrix(camera):

    position = [coordinate for coordinate in camera.location]
    rotation = [degrees(angle) for angle in camera.rotation_euler]

    return np.matmul(translate_matrix(position), rotate_matrix(rotation))
