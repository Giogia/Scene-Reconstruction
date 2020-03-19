from math import radians
from mathutils import Vector
from bpy import context, ops
from random import random

from .parameters import *


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
