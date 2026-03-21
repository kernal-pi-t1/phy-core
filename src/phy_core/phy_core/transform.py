"""Fixed-camera extrinsic coordinate transform (camera frame -> base frame).

Pipeline:
    RGB+Depth -> 2D pixel -> 3D camera coord -> 3D base coord (= goal)

Camera optical frame (OpenCV): X-right, Y-down, Z-forward(depth)
Base frame (Doosan):           X-forward, Y-left, Z-up

Transform:
    P_base     = R_cam @ P_cam + t_cam
    R_obj_base = R_cam @ R_obj_cam

With camera_rpy=[180,0,0] (downward-looking):
    R_cam = [[1,0,0],[0,-1,0],[0,0,-1]]
    cam_X ->  base_X
    cam_Y -> -base_Y
    cam_Z -> -base_Z
"""

import math
import numpy as np


def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Euler XYZ (radians) -> 3x3 rotation matrix."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp,     cp * sr,                cp * cr],
    ])


def rotation_matrix_to_euler(R: np.ndarray) -> tuple:
    """3x3 rotation matrix -> Euler XYZ (radians) as (roll, pitch, yaw)."""
    pitch = math.asin(np.clip(-R[2, 0], -1.0, 1.0))
    if abs(math.cos(pitch)) > 1e-6:
        roll = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        roll = math.atan2(-R[1, 2], R[1, 1])
        yaw = 0.0
    return roll, pitch, yaw


class CameraToBaseTransform:
    """Fixed camera -> robot base frame coordinate transform.

    Args:
        offset: [x, y, z] meters, camera position in base frame.
        rpy_deg: [roll, pitch, yaw] degrees, camera orientation in base frame.
    """

    def __init__(self, offset: list, rpy_deg: list):
        self.offset = np.array(offset, dtype=np.float64)
        rpy_rad = [math.radians(v) for v in rpy_deg]
        self.R_cam = euler_to_rotation_matrix(*rpy_rad)

    def transform_pose(self, camera_pose: list) -> list:
        """Transform [x,y,z,roll,pitch,yaw] from camera frame to base frame.

        Input orientation (roll,pitch,yaw) is in radians (from PCA).
        Output orientation is also in radians.
        """
        p_cam = np.array(camera_pose[:3])

        # Position: rotate then translate
        p_base = self.R_cam @ p_cam + self.offset

        # Orientation: compose rotations
        R_obj_cam = euler_to_rotation_matrix(
            camera_pose[3], camera_pose[4], camera_pose[5]
        )
        R_obj_base = self.R_cam @ R_obj_cam
        roll, pitch, yaw = rotation_matrix_to_euler(R_obj_base)

        return [
            float(p_base[0]), float(p_base[1]), float(p_base[2]),
            float(roll), float(pitch), float(yaw),
        ]
