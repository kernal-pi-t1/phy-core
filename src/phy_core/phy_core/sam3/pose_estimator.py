"""6DoF Pose Estimation using Sam3FastProcessor + depth PCA.

Thin wrapper that combines Sam3FastProcessor with depth-based PCA pose estimation.
"""

import os
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import yaml
from PIL import Image
from scipy.spatial.transform import Rotation as R

logger = logging.getLogger(__name__)

_CROP_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "crop_config.yaml"
)


@dataclass
class ObjectPose:
    """6DoF object pose in OpenCV camera frame (X-right, Y-down, Z-forward)."""
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float
    method: str


def load_crop_config(config_path=_CROP_CONFIG_PATH):
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy):
    vs, us = np.where(mask)
    z_mm = depth_mm[vs, us].astype(np.float64)
    valid = z_mm > 0
    us, vs, z_mm = us[valid], vs[valid], z_mm[valid]
    z = z_mm / 1000.0
    x = (us.astype(np.float64) - cx) * z / fx
    y = (vs.astype(np.float64) - cy) * z / fy
    return np.stack([x, y, z], axis=-1)


def compute_centroid(points_3d):
    if len(points_3d) == 0:
        raise ValueError("No valid 3D points")
    c = points_3d.mean(axis=0)
    return float(c[0]), float(c[1]), float(c[2])


def pca_rotation_with_gravity(points_3d):
    centered = points_3d - points_3d.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    if eigenvalues[0] <= 0:
        return np.eye(3)
    if eigenvalues[2] / eigenvalues[0] < 1e-6:
        return np.eye(3)

    gravity_up = np.array([0.0, -1.0, 0.0])
    if np.dot(eigenvectors[:, 2], gravity_up) < 0:
        eigenvectors[:, 2] *= -1
    if np.linalg.det(eigenvectors) < 0:
        eigenvectors[:, 1] *= -1
    return eigenvectors


def camera_to_base(x, y, z):
    """Convert camera-frame position to robot base-frame position.

    Camera is mounted at offset (90, 4, 66) mm from the robot base origin.
    """
    return x + 90.0, y + 4.0, z + 66.0


def rotation_matrix_to_rpy(R_mat):
    rpy = R.from_matrix(R_mat).as_euler('xyz', degrees=True)
    return float(rpy[0]), float(rpy[1]), float(rpy[2])


class PoseEstimator:
    """6DoF pose estimation using Sam3FastProcessor + depth PCA."""

    def __init__(self, device="cuda", confidence_threshold=0.5,
                 frame_skip=1, crop_config_path=_CROP_CONFIG_PATH):
        from .processor import Sam3FastProcessor
        self._sam3 = Sam3FastProcessor(
            device=device,
            confidence_threshold=confidence_threshold,
            frame_skip=frame_skip,
        )
        self._crop = load_crop_config(crop_config_path)
        if self._crop:
            x1, y1, x2, y2 = self._crop
            logger.info("Crop region: (%d,%d)-(%d,%d)", x1, y1, x2, y2)

    def estimate_poses(
        self,
        rgb_or_bgr: np.ndarray,
        depth_mm: np.ndarray,
        intrinsics: Tuple[float, float, float, float],
        prompt: str = "object",
        is_bgr: bool = True,
    ) -> List[ObjectPose]:
        if self._crop:
            x1, y1, x2, y2 = self._crop
            rgb_or_bgr = rgb_or_bgr[y1:y2, x1:x2].copy()
            depth_mm = depth_mm[y1:y2, x1:x2].copy()
            fx, fy, cx, cy = intrinsics
            intrinsics = (fx, fy, cx - x1, cy - y1)

        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr
        pil_image = Image.fromarray(rgb)

        state = self._sam3.segment(pil_image, prompt=prompt)
        masks = state.get("masks")

        if masks is None or len(masks) == 0:
            logger.warning("No objects detected for prompt '%s'", prompt)
            return []

        masks_np = masks.squeeze(1).cpu().numpy().astype(bool)
        fx, fy, cx, cy = intrinsics
        poses = []

        for i in range(len(masks_np)):
            mask = masks_np[i]
            if not mask.any():
                continue
            points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)
            if len(points) < 3:
                continue
            x, y, z = compute_centroid(points)
            R_mat = pca_rotation_with_gravity(points)
            roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)
            poses.append(ObjectPose(x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="sam3_pca"))

        logger.info("Detected %d masks, estimated %d poses", len(masks_np), len(poses))
        return poses

    def invalidate_cache(self):
        """Force backbone recomputation on next call."""
        self._sam3.invalidate_cache()
