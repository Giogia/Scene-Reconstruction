import time
import os
import numpy as np

from csv_utils import read_csv
from exr_utils import exr_to_depth, exr_to_image
from parameters import TEST_SAMPLES, DISTANCE

from tsdf_fusion import get_view_frustum, TSDFVolume, meshwrite

from visualization import show_array


def fuse(name):

    path = os.path.join(os.getcwd(), '../test', name)

    print("Estimating voxel volume bounds...")
    images = TEST_SAMPLES

    camera_intrinsics_file = os.path.join(path, 'camera_intrinsics.csv')
    camera_intrinsics = np.reshape(read_csv(file=camera_intrinsics_file), (3, 3))

    bounds = np.zeros((3, 2))

    for i in range(0, images):

        name = str(i+1)

        image_file = os.path.join(path, name + '.exr')
        depth = exr_to_depth(image_file, far_threshold=2*DISTANCE)

        camera_pose_file = os.path.join(path, name + '_pose.csv')
        camera_pose = np.reshape(np.array(
            read_csv(file=camera_pose_file), dtype=float), (4, 4))

        # Compute camera view frustum and extend convex hull
        frustum_points = get_view_frustum(depth, camera_intrinsics, camera_pose)
        bounds[:, 0] = np.minimum(bounds[:, 0], np.amin(frustum_points, axis=1))
        bounds[:, 1] = np.maximum(bounds[:, 1], np.amax(frustum_points, axis=1))

    print("Initializing voxel volume...")
    tsdf_volume = TSDFVolume(bounds, voxel_size=0.05)

    # Loop through RGB-D images and fuse them together
    t0_elapse = time.time()

    for i in range(0, images):
        print("Fusing frame %d/%d" % (i + 1, images))

        # Read RGB-D image and camera pose
        image_file = os.path.join(path, str(i + 1) + '.exr')

        color = exr_to_image(image_file)
        depth = exr_to_depth(image_file, far_threshold=2*DISTANCE)

        show_array(color)
        show_array(depth)

        camera_pose = np.reshape(np.array(
            read_csv(file=camera_pose_file), dtype=float), (4, 4))

        # Integrate observation into voxel volume (assume color aligned with depth)
        tsdf_volume.integrate(color, depth, camera_intrinsics, camera_pose, obs_weight=1.)

        # Save intermediate models
        vertices, faces, norms, colors = tsdf_volume.get_mesh()
        saving_path = os.path.join(path, 'mesh.ply')
        meshwrite(saving_path, vertices, faces, norms, colors)

    fps = images / (time.time() - t0_elapse)
    print("Average FPS: {:.2f}".format(fps))

    # Get mesh from voxel volume and save to disk (can be viewed with Meshlab)
    print("Saving mesh to mesh.ply...")
    vertices, faces, norms, colors = tsdf_volume.get_mesh()

    saving_path = os.path.join(path, 'mesh.ply')
    meshwrite(saving_path, vertices, faces, norms, colors)

    # Get point cloud from voxel volume and save to disk (can be viewed with Meshlab)
    # print("Saving point cloud to pc.ply...")
    # point_cloud = tsdf_volume.get_point_cloud()
    # fusion.pcwrite("pc.ply", point_cloud)


fuse('Fly')
