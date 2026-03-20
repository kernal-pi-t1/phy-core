"""
6DoF Pose Estimation: SAM 3 + RealSense Depth PCA

Estimates object pose (x, y, z, roll, pitch, yaw) in the camera coordinate frame
(OpenCV convention: X-right, Y-down, Z-forward) using SAM 3 for segmentation
and PCA on RealSense depth point clouds for orientation with gravity correction.

Two usage modes:
  - estimate_poses():        SAM 3 text-prompt segmentation → N masks → N poses
  - estimate_pose_from_mask(): External pre-computed mask → single pose (PCA only)

Usage:
    from pose_estimator import PoseEstimator, ObjectPose

    estimator = PoseEstimator(device="cuda")
    poses = estimator.estimate_poses(color_bgr, depth_mm, (fx, fy, cx, cy), prompt="object")
"""

import sys
import os
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import torch
import yaml
from PIL import Image
from scipy.spatial.transform import Rotation as R

_this_dir = os.path.dirname(os.path.abspath(__file__))
_CROP_CONFIG_PATH = os.path.join(_this_dir, "crop_config.yaml")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class ObjectPose:
    """6DoF object pose in OpenCV camera frame (X-right, Y-down, Z-forward)."""
    x: float        # meters
    y: float        # meters
    z: float        # meters
    roll: float     # degrees
    pitch: float    # degrees
    yaw: float      # degrees
    method: str     # "sam3_pca" or "pca"


# ---------------------------------------------------------------------------
# Pure utility functions (independently testable)
# ---------------------------------------------------------------------------

def load_crop_config(config_path: str = _CROP_CONFIG_PATH) -> Optional[Tuple[int, int, int, int]]:
    """Load crop region from config file. Returns (x1, y1, x2, y2) or None."""
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def validate_inputs(
    rgb: np.ndarray,
    depth_mm: np.ndarray,
    mask: np.ndarray | None = None,
) -> np.ndarray | None:
    """Validate and normalize inputs. Returns the (possibly squeezed) mask, or None."""
    if depth_mm.dtype != np.uint16:
        raise ValueError(f"Depth must be uint16 (mm), got {depth_mm.dtype}")
    if rgb.shape[:2] != depth_mm.shape[:2]:
        raise ValueError(
            f"RGB spatial dims {rgb.shape[:2]} != depth dims {depth_mm.shape[:2]}"
        )
    if mask is None:
        return None
    if mask.ndim == 3 and mask.shape[2] == 1:
        mask = mask[:, :, 0]
    if mask.ndim != 2:
        raise ValueError(f"Mask must be 2D (H,W), got shape {mask.shape}")
    if mask.shape != depth_mm.shape:
        raise ValueError(
            f"Mask shape {mask.shape} != depth shape {depth_mm.shape}"
        )
    if not mask.any():
        raise ValueError("Mask is entirely empty (no True pixels)")
    return mask


def deproject_depth_to_points(
    depth_mm: np.ndarray,
    mask: np.ndarray,
    fx: float, fy: float, cx: float, cy: float,
) -> np.ndarray:
    """Deproject masked depth pixels to 3D points in OpenCV camera frame.

    Args:
        depth_mm: (H, W) uint16 depth in millimeters.
        mask: (H, W) boolean mask selecting the object region.
        fx, fy, cx, cy: Camera intrinsics.

    Returns:
        (N, 3) float64 array of 3D points in meters.
        Points with zero depth are excluded.
    """
    if fx <= 0 or fy <= 0:
        raise ValueError(f"Focal lengths must be positive: fx={fx}, fy={fy}")

    vs, us = np.where(mask)
    z_mm = depth_mm[vs, us].astype(np.float64)

    valid = z_mm > 0
    us, vs, z_mm = us[valid], vs[valid], z_mm[valid]

    z = z_mm / 1000.0
    x = (us.astype(np.float64) - cx) * z / fx
    y = (vs.astype(np.float64) - cy) * z / fy

    return np.stack([x, y, z], axis=-1)


def compute_centroid(points_3d: np.ndarray) -> Tuple[float, float, float]:
    """Compute mean position of 3D points.

    Args:
        points_3d: (N, 3) array in meters.

    Returns:
        (x, y, z) centroid in meters.
    """
    if len(points_3d) == 0:
        raise ValueError("No valid 3D points to compute centroid")
    c = points_3d.mean(axis=0)
    return float(c[0]), float(c[1]), float(c[2])


def pca_rotation_with_gravity(points_3d: np.ndarray) -> np.ndarray:
    """Compute rotation matrix from PCA on 3D points with gravity correction.

    Steps:
    1. PCA → 3 eigenvectors sorted by eigenvalue (descending)
    2. PC1 = longest axis, PC2 = second, PC3 = shortest (surface normal)
    3. Gravity correction: PC3 aligns with -Y (up in OpenCV camera frame)
    4. Enforce right-hand rule: det(R) = 1

    Returns (3, 3) rotation matrix. Returns identity with warning for
    degenerate point clouds.
    """
    centered = points_3d - points_3d.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # eigh returns ascending; reverse to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Degenerate guard: all-zero eigenvalues (identical points)
    if eigenvalues[0] <= 0:
        logger.warning("All eigenvalues <= 0 (identical points). Returning identity rotation.")
        return np.eye(3)

    # Degenerate guard: near-singular covariance (collinear or planar)
    if eigenvalues[2] / eigenvalues[0] < 1e-6:
        logger.warning(
            "Degenerate point cloud (eigenvalue ratio %.2e). "
            "Returning identity rotation.", eigenvalues[2] / eigenvalues[0]
        )
        return np.eye(3)

    # Gravity correction: PC3 (normal) should point roughly upward (-Y in camera frame)
    gravity_up = np.array([0.0, -1.0, 0.0])
    if np.dot(eigenvectors[:, 2], gravity_up) < 0:
        eigenvectors[:, 2] *= -1

    # Enforce right-hand rule: det(R) must be +1
    if np.linalg.det(eigenvectors) < 0:
        eigenvectors[:, 1] *= -1

    return eigenvectors


def rotation_matrix_to_rpy(R_mat: np.ndarray) -> Tuple[float, float, float]:
    """Convert 3x3 rotation matrix to roll, pitch, yaw in degrees."""
    rpy = R.from_matrix(R_mat).as_euler('xyz', degrees=True)
    return float(rpy[0]), float(rpy[1]), float(rpy[2])


# ---------------------------------------------------------------------------
# PoseEstimator class
# ---------------------------------------------------------------------------

class PoseEstimator:
    """6DoF pose estimation using SAM 3 segmentation + depth PCA.

    Two usage modes:
    1. estimate_poses(): SAM 3 text-prompt segmentation → N masks → N poses
    2. estimate_pose_from_mask(): External mask → single pose (no SAM 3)
    """

    def __init__(self, device: str = "cuda", confidence_threshold: float = 0.5,
                 crop_config_path: str = _CROP_CONFIG_PATH):
        # Lazy import: SAM 3 dependencies only needed when instantiating
        sys.path.insert(0, os.path.join(_this_dir, "sam3"))
        from sam3 import build_sam3_image_model
        from sam3.model.sam3_image_processor import Sam3Processor

        # Performance: enable cudnn benchmark + torch.compile
        torch.backends.cudnn.benchmark = True

        model = build_sam3_image_model(
            device=device, eval_mode=True, compile=True,
        )
        self._processor = Sam3Processor(
            model, device=device, confidence_threshold=confidence_threshold
        )
        self._device = device
        self._cached_text = {}  # prompt → text features cache

        # Load fixed crop region (set via select_crop_region.py)
        self._crop = load_crop_config(crop_config_path)
        if self._crop:
            x1, y1, x2, y2 = self._crop
            logger.info("Crop region loaded: (%d,%d)-(%d,%d) [%dx%d]",
                        x1, y1, x2, y2, x2 - x1, y2 - y1)
        else:
            logger.info("No crop config found, using full image")

    def estimate_poses(
        self,
        rgb_or_bgr: np.ndarray,
        depth_mm: np.ndarray,
        intrinsics: Tuple[float, float, float, float],
        prompt: str = "object",
        is_bgr: bool = True,
    ) -> List[ObjectPose]:
        """Estimate 6DoF poses for all objects matching the text prompt.

        Args:
            rgb_or_bgr: (H, W, 3) uint8 color image.
            depth_mm: (H, W) uint16 depth in millimeters.
            intrinsics: (fx, fy, cx, cy) camera intrinsics.
            prompt: Text prompt for SAM 3 (e.g., "object", "cup", "box").
            is_bgr: If True, convert BGR→RGB before SAM 3.

        Returns:
            List[ObjectPose] for each detected object. Empty list if none found.
        """
        validate_inputs(rgb_or_bgr, depth_mm)

        # Apply fixed crop region if configured
        if self._crop:
            x1, y1, x2, y2 = self._crop
            rgb_or_bgr = rgb_or_bgr[y1:y2, x1:x2].copy()
            depth_mm = depth_mm[y1:y2, x1:x2].copy()
            # Adjust intrinsics for crop offset
            fx, fy, cx, cy = intrinsics
            intrinsics = (fx, fy, cx - x1, cy - y1)

        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr
        pil_image = Image.fromarray(rgb)

        with torch.amp.autocast('cuda', dtype=torch.float16):
            state = self._processor.set_image(pil_image)
            # Cache text features per prompt to avoid recomputation
            if prompt not in self._cached_text:
                self._cached_text[prompt] = (
                    self._processor.model.backbone.forward_text(
                        [prompt], device=self._device
                    )
                )
            state["backbone_out"].update(self._cached_text[prompt])
            if "geometric_prompt" not in state:
                state["geometric_prompt"] = self._processor.model._get_dummy_prompt()
            state = self._processor._forward_grounding(state)

        masks = state["masks"]  # (N, 1, H, W) from sam3_image_processor.py:219

        if masks is None or len(masks) == 0:
            logger.warning("SAM 3 detected no objects for prompt '%s'", prompt)
            return []

        masks_np = masks.squeeze(1).cpu().numpy().astype(bool)  # (N, H, W)
        fx, fy, cx, cy = intrinsics
        poses = []

        for i in range(len(masks_np)):
            mask = masks_np[i]
            if not mask.any():
                logger.warning("Mask %d is empty, skipping", i)
                continue

            points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)
            if len(points) < 3:
                logger.warning(
                    "Mask %d has only %d valid depth points, skipping", i, len(points)
                )
                continue

            x, y, z = compute_centroid(points)
            R_mat = pca_rotation_with_gravity(points)
            roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

            poses.append(ObjectPose(
                x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="sam3_pca"
            ))

        logger.info("Detected %d objects, estimated %d poses", len(masks_np), len(poses))
        return poses

    def estimate_pose_from_mask(
        self,
        depth_mm: np.ndarray,
        mask: np.ndarray,
        intrinsics: Tuple[float, float, float, float],
    ) -> ObjectPose:
        """Estimate 6DoF pose from a pre-computed mask (no SAM 3 needed).

        Args:
            depth_mm: (H, W) uint16 depth in mm.
            mask: (H, W) binary mask for target object.
            intrinsics: (fx, fy, cx, cy).

        Returns:
            ObjectPose with method="pca".

        Raises:
            ValueError: If inputs are invalid or insufficient depth points.
        """
        if mask.ndim == 3 and mask.shape[2] == 1:
            mask = mask[:, :, 0]
        if mask.ndim != 2:
            raise ValueError(f"Mask must be 2D, got shape {mask.shape}")
        if depth_mm.dtype != np.uint16:
            raise ValueError(f"Depth must be uint16, got {depth_mm.dtype}")
        if mask.shape != depth_mm.shape:
            raise ValueError(f"Mask {mask.shape} != depth {depth_mm.shape}")
        if not mask.any():
            raise ValueError("Mask is empty")

        fx, fy, cx, cy = intrinsics
        points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)
        if len(points) < 3:
            raise ValueError(f"Only {len(points)} valid depth points, need >= 3")

        x, y, z = compute_centroid(points)
        R_mat = pca_rotation_with_gravity(points)
        roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

        return ObjectPose(x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="pca")


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import cv2

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="6DoF pose estimation with SAM 3 + PCA")
    parser.add_argument("--prompt", default="object", help="SAM 3 text prompt (default: object)")
    parser.add_argument("--mask", default=None, help="Path to external mask PNG (skips SAM 3)")
    parser.add_argument("--device", default="cuda", help="torch device")
    parser.add_argument("--confidence", type=float, default=0.5, help="SAM 3 confidence threshold")
    parser.add_argument("--fx", type=float, default=None)
    parser.add_argument("--fy", type=float, default=None)
    parser.add_argument("--cx", type=float, default=None)
    parser.add_argument("--cy", type=float, default=None)
    args = parser.parse_args()


    # --- Capture from RealSense ---
    from capture_realsense import capture_single_frame
    depth_mm, color_bgr = capture_single_frame()
    print(f"Captured: color {color_bgr.shape}, depth {depth_mm.shape}")

    # --- Intrinsics (from args or auto-detect) ---
    if all(v is not None for v in [args.fx, args.fy, args.cx, args.cy]):
        intrinsics = (args.fx, args.fy, args.cx, args.cy)
    else:
        import pyrealsense2 as rs
        print("Auto-detecting intrinsics (provide --fx/--fy/--cx/--cy to skip)...")
        try:
            pipe = rs.pipeline()
            cfg = rs.config()
            cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            profile = pipe.start(cfg)
            intr = profile.get_stream(
                rs.stream.color
            ).as_video_stream_profile().get_intrinsics()
            pipe.stop()
            intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)
            print(f"Auto-detected intrinsics: fx={intr.fx:.1f}, fy={intr.fy:.1f}, "
                  f"cx={intr.ppx:.1f}, cy={intr.ppy:.1f}")
        except RuntimeError as e:
            print(f"ERROR: Failed to auto-detect intrinsics: {e}", file=sys.stderr)
            print("Please provide --fx, --fy, --cx, --cy manually.", file=sys.stderr)
            sys.exit(1)

    # --- Estimate pose ---
    estimator = PoseEstimator(device=args.device, confidence_threshold=args.confidence)

    if args.mask:
        # External mask mode (no SAM 3 segmentation)
        mask_raw = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
        if mask_raw is None:
            print(f"ERROR: Failed to read mask image: {args.mask}", file=sys.stderr)
            sys.exit(1)
        mask = mask_raw > 0
        print(f"Mask: {mask.shape}, {mask.sum()} pixels selected")
        pose = estimator.estimate_pose_from_mask(depth_mm, mask, intrinsics)
        print(f"\n[PCA]  x={pose.x:.4f}m  y={pose.y:.4f}m  z={pose.z:.4f}m  "
              f"roll={pose.roll:.2f}\u00b0  pitch={pose.pitch:.2f}\u00b0  yaw={pose.yaw:.2f}\u00b0")
    else:
        # SAM 3 text-prompt segmentation mode
        print(f"Running SAM 3 segmentation with prompt: '{args.prompt}'")
        poses = estimator.estimate_poses(
            color_bgr, depth_mm, intrinsics, prompt=args.prompt
        )
        if not poses:
            print("No objects detected.")
        for i, pose in enumerate(poses):
            print(f"[Object {i}]  x={pose.x:.4f}m  y={pose.y:.4f}m  z={pose.z:.4f}m  "
                  f"roll={pose.roll:.2f}\u00b0  pitch={pose.pitch:.2f}\u00b0  yaw={pose.yaw:.2f}\u00b0")
