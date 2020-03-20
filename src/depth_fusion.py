"""Fuse 1000 RGB-D images from the 7-scenes dataset into a TSDF voxel volume with 2cm resolution.
"""

import time
import os
import cv2
import numpy as np

from csv_utils import read_csv

import fusion
from exr_utils import exr_to_depth, exr_to_array

PATH = os.getcwd()

name = 'Fox'

if __name__ == "__main__":

    print("Estimating voxel volume bounds...")
    images = 5

    camera_calibration_file = os.path.join(PATH, '../test', name, 'camera_calibration.csv')
    camera_intrinsics = np.reshape(read_csv(file=camera_calibration_file, field='Camera Intrinsics'), (3, 3))

    bounds = np.zeros((3, 2))

    for i in range(images):

        path = os.path.join(PATH, '../test', name, str(i+1) + '.exr')
        depth = exr_to_depth(path)

        camera_pose_file = os.path.join(PATH, '../test', name, 'frames.csv')
        camera_pose = np.reshape(np.array(
            read_csv(file=camera_pose_file, field='Matrix', row_number=i), dtype=float), (4, 4))

        # Compute camera view frustum and extend convex hull
        view_frust_pts = fusion.get_view_frustum(depth, camera_intrinsics, camera_pose)
        bounds[:, 0] = np.minimum(bounds[:, 0], np.amin(view_frust_pts, axis=1))
        bounds[:, 1] = np.maximum(bounds[:, 1], np.amax(view_frust_pts, axis=1))

    print("Initializing voxel volume...")
    tsdf_vol = fusion.TSDFVolume(bounds, voxel_size=0.02)

    # Loop through RGB-D images and fuse them together
    t0_elapse = time.time()

    for i in range(images):
        print("Fusing frame %d/%d" % (i + 1, images))

        # Read RGB-D image and camera pose
        path = os.path.join(PATH, '../test', name, str(i + 1) + '.exr')
        color_image = exr_to_array(path)
        depth = exr_to_depth(path)

        camera_pose = np.reshape(np.array(
            read_csv(file=camera_pose_file, field='Matrix', row_number=i), dtype=float), (4, 4))

        # Integrate observation into voxel volume (assume color aligned with depth)
        tsdf_vol.integrate(color_image, depth, camera_intrinsics, camera_pose, obs_weight=1.)

    fps = images / (time.time() - t0_elapse)
    print("Average FPS: {:.2f}".format(fps))

    # Get mesh from voxel volume and save to disk (can be viewed with Meshlab)
    print("Saving mesh to mesh.ply...")
    verts, faces, norms, colors = tsdf_vol.get_mesh()
    fusion.meshwrite("mesh.ply", verts, faces, norms, colors)

    # Get point cloud from voxel volume and save to disk (can be viewed with Meshlab)
    print("Saving point cloud to pc.ply...")
    point_cloud = tsdf_vol.get_point_cloud()
    fusion.pcwrite("pc.ply", point_cloud)
