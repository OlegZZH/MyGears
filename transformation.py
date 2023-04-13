from pyrr import Matrix44
import numpy as np
def rot_z(points,angle):
    return points.dot(Matrix44.from_z_rotation(np.deg2rad(angle))[:2,:2])

