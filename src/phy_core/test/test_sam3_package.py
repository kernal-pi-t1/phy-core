"""Unit tests for phy_core.sam3 package (no GPU/model required)."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np


class TestPoseEstimatorUtils(unittest.TestCase):
    """Test pure utility functions in pose_estimator module."""

    def test_deproject_depth_to_points(self):
        from phy_core.sam3.pose_estimator import deproject_depth_to_points

        depth = np.zeros((4, 4), dtype=np.uint16)
        depth[1, 2] = 1000  # 1 meter
        depth[2, 3] = 2000  # 2 meters
        mask = depth > 0

        points = deproject_depth_to_points(depth, mask, fx=100, fy=100, cx=2, cy=2)
        assert points.shape == (2, 3)
        # Point at (2,1) with depth 1m: x=(2-2)*1/100=0, y=(1-2)*1/100=-0.01, z=1.0
        np.testing.assert_allclose(points[0], [0.0, -0.01, 1.0])

    def test_deproject_excludes_zero_depth(self):
        from phy_core.sam3.pose_estimator import deproject_depth_to_points

        depth = np.zeros((4, 4), dtype=np.uint16)
        mask = np.ones((4, 4), dtype=bool)  # all True, but all zero depth

        points = deproject_depth_to_points(depth, mask, fx=100, fy=100, cx=2, cy=2)
        assert len(points) == 0

    def test_compute_centroid(self):
        from phy_core.sam3.pose_estimator import compute_centroid

        pts = np.array([[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]])
        x, y, z = compute_centroid(pts)
        assert x == 2.0
        assert y == 3.0
        assert z == 4.0

    def test_compute_centroid_empty_raises(self):
        from phy_core.sam3.pose_estimator import compute_centroid

        with self.assertRaises(ValueError):
            compute_centroid(np.array([]).reshape(0, 3))

    def test_pca_rotation_returns_valid_rotation(self):
        from phy_core.sam3.pose_estimator import pca_rotation_with_gravity

        rng = np.random.RandomState(42)
        pts = rng.randn(100, 3) * [3.0, 1.0, 0.5]  # elongated along X
        R = pca_rotation_with_gravity(pts)
        assert R.shape == (3, 3)
        # Must be a valid rotation: det(R) ≈ 1
        np.testing.assert_allclose(np.linalg.det(R), 1.0, atol=1e-6)
        # R^T @ R ≈ I
        np.testing.assert_allclose(R.T @ R, np.eye(3), atol=1e-6)

    def test_pca_degenerate_returns_identity(self):
        from phy_core.sam3.pose_estimator import pca_rotation_with_gravity

        pts = np.ones((10, 3))  # all identical
        R = pca_rotation_with_gravity(pts)
        np.testing.assert_array_equal(R, np.eye(3))

    def test_rotation_matrix_to_rpy(self):
        from phy_core.sam3.pose_estimator import rotation_matrix_to_rpy

        roll, pitch, yaw = rotation_matrix_to_rpy(np.eye(3))
        assert abs(roll) < 1e-6
        assert abs(pitch) < 1e-6
        assert abs(yaw) < 1e-6

    def test_load_crop_config_missing_file(self):
        from phy_core.sam3.pose_estimator import load_crop_config

        result = load_crop_config("/nonexistent/path.yaml")
        assert result is None


class TestObjectPose(unittest.TestCase):
    """Test ObjectPose dataclass."""

    def test_fields(self):
        from phy_core.sam3.pose_estimator import ObjectPose

        p = ObjectPose(x=1.0, y=2.0, z=3.0, roll=10.0, pitch=20.0, yaw=30.0, method="test")
        assert p.x == 1.0
        assert p.method == "test"


class TestSam3FastProcessor(unittest.TestCase):
    """Test Sam3FastProcessor without loading the actual model."""

    def _make_processor(self, frame_skip=5):
        import phy_core.sam3.processor as mod
        proc = mod.Sam3FastProcessor.__new__(mod.Sam3FastProcessor)
        proc._processor = MagicMock()
        proc._device = 'cpu'
        proc._cached_text = {}
        proc._cached_backbone = None
        proc._frame_skip = frame_skip
        proc._frame_count = 0
        return proc

    def test_attributes(self):
        proc = self._make_processor(frame_skip=5)
        assert proc._frame_skip == 5
        assert proc._cached_backbone is None
        assert proc._frame_count == 0
        assert proc._cached_text == {}

    def test_invalidate_cache(self):
        proc = self._make_processor()
        proc._cached_backbone = {"some": "data"}
        proc._frame_count = 10

        proc.invalidate_cache()

        assert proc._cached_backbone is None
        assert proc._frame_count == 0


class TestPoseEstimatorIntegration(unittest.TestCase):
    """Test PoseEstimator with mocked Sam3FastProcessor."""

    def _make_estimator(self):
        """Create PoseEstimator with mocked processor."""
        import phy_core.sam3.pose_estimator as mod

        with patch.object(mod, 'Sam3FastProcessor', create=True) as MockProc:
            # Prevent __init__ from actually loading the model
            with patch('phy_core.sam3.pose_estimator.Sam3FastProcessor') as MP:
                estimator = mod.PoseEstimator.__new__(mod.PoseEstimator)
                estimator._sam3 = MagicMock()
                estimator._crop = None
                return estimator

    def test_estimate_poses_no_masks(self):
        estimator = self._make_estimator()
        estimator._sam3.segment.return_value = {"masks": None}

        rgb = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.zeros((480, 640), dtype=np.uint16)
        result = estimator.estimate_poses(rgb, depth, (600, 600, 320, 240), is_bgr=False)

        assert result == []

    def test_estimate_poses_empty_masks(self):
        import torch
        estimator = self._make_estimator()
        estimator._sam3.segment.return_value = {"masks": torch.zeros(0, 1, 480, 640)}

        rgb = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.zeros((480, 640), dtype=np.uint16)
        result = estimator.estimate_poses(rgb, depth, (600, 600, 320, 240), is_bgr=False)

        assert result == []

    def test_estimate_poses_with_valid_mask(self):
        import torch
        estimator = self._make_estimator()

        # Create a mask with some pixels set
        mask_tensor = torch.zeros(1, 1, 480, 640, dtype=torch.bool)
        mask_tensor[0, 0, 200:210, 300:310] = True

        estimator._sam3.segment.return_value = {"masks": mask_tensor}

        rgb = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.ones((480, 640), dtype=np.uint16) * 1000  # 1m everywhere

        result = estimator.estimate_poses(
            rgb, depth, (600.0, 600.0, 320.0, 240.0), is_bgr=False
        )

        assert len(result) == 1
        assert result[0].method == "sam3_pca"
        assert result[0].z > 0  # should have positive depth

    def test_invalidate_cache_delegates(self):
        estimator = self._make_estimator()
        estimator.invalidate_cache()
        estimator._sam3.invalidate_cache.assert_called_once()
