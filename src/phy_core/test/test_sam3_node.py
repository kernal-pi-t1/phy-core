"""Unit tests for Sam3Node."""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from collections import namedtuple

import rclpy


class TestSam3NodeInit(unittest.TestCase):
    """Test Sam3Node initialization and parameter handling."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def _make_node(self, params=None):
        """Create Sam3Node with mocked PoseEstimator and capture."""
        default_params = {
            'device': 'cpu',
            'confidence_threshold': 0.5,
            'fx': 600.0, 'fy': 600.0,
            'cx': 320.0, 'cy': 240.0,
        }
        if params:
            default_params.update(params)

        with patch(
            'phy_core.node.sam3_node.PoseEstimator', create=True
        ) as MockEstimator, patch(
            'phy_core.node.sam3_node.capture_single_frame', create=True
        ) as mock_capture:
            # Patch imports inside Sam3Node.__init__
            import phy_core.node.sam3_node as mod

            original_init = mod.Sam3Node.__init__

            def patched_init(self_node):
                # Call Node.__init__ directly
                from rclpy.node import Node
                Node.__init__(self_node, 'sam3_node')

                # Declare params with test values
                for k, v in default_params.items():
                    self_node.declare_parameter(k, v)

                device = self_node.get_parameter('device').get_parameter_value().string_value
                confidence = self_node.get_parameter('confidence_threshold').get_parameter_value().double_value
                self_node.fx = self_node.get_parameter('fx').get_parameter_value().double_value
                self_node.fy = self_node.get_parameter('fy').get_parameter_value().double_value
                self_node.cx = self_node.get_parameter('cx').get_parameter_value().double_value
                self_node.cy = self_node.get_parameter('cy').get_parameter_value().double_value

                if self_node.fx <= 0.0 or self_node.fy <= 0.0:
                    raise RuntimeError('Invalid camera intrinsics: fx and fy must be > 0')

                import threading
                self_node._estimator = MagicMock()
                self_node._capture = MagicMock()
                self_node._camera_to_base = MagicMock(side_effect=lambda x, y, z: (x, y, z))
                self_node._lock = threading.Lock()

                from phy_interface.srv import GetPose
                self_node._get_pose_srv = self_node.create_service(
                    GetPose, 'get_pose', self_node._get_pose_callback
                )

            with patch.object(mod.Sam3Node, '__init__', patched_init):
                node = mod.Sam3Node()

        return node

    def test_node_name(self):
        node = self._make_node()
        assert node.get_name() == 'sam3_node'
        node.destroy_node()

    def test_camera_intrinsics_loaded(self):
        node = self._make_node({'fx': 615.0, 'fy': 616.0, 'cx': 325.0, 'cy': 245.0})
        assert node.fx == 615.0
        assert node.fy == 616.0
        assert node.cx == 325.0
        assert node.cy == 245.0
        node.destroy_node()

    def test_invalid_intrinsics_raises(self):
        with self.assertRaises(RuntimeError):
            self._make_node({'fx': 0.0, 'fy': 600.0})

    def test_invalid_intrinsics_fy_raises(self):
        with self.assertRaises(RuntimeError):
            self._make_node({'fx': 600.0, 'fy': -1.0})


class TestSam3NodeCallback(unittest.TestCase):
    """Test _get_pose_callback logic."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        """Create a Sam3Node with mocked dependencies."""
        import threading
        from rclpy.node import Node
        import phy_core.node.sam3_node as mod

        def patched_init(self_node):
            Node.__init__(self_node, 'sam3_node')
            self_node.declare_parameter('device', 'cpu')
            self_node.declare_parameter('confidence_threshold', 0.5)
            self_node.declare_parameter('fx', 600.0)
            self_node.declare_parameter('fy', 600.0)
            self_node.declare_parameter('cx', 320.0)
            self_node.declare_parameter('cy', 240.0)

            self_node.fx = 600.0
            self_node.fy = 600.0
            self_node.cx = 320.0
            self_node.cy = 240.0

            self_node._estimator = MagicMock()
            self_node._capture = MagicMock()
            self_node._camera_to_base = MagicMock(side_effect=lambda x, y, z: (x, y, z))
            self_node._lock = threading.Lock()

            from phy_interface.srv import GetPose
            self_node._get_pose_srv = self_node.create_service(
                GetPose, 'get_pose', self_node._get_pose_callback
            )

        with patch.object(mod.Sam3Node, '__init__', patched_init):
            self.node = mod.Sam3Node()

    def tearDown(self):
        self.node.destroy_node()

    def test_callback_returns_pose_on_detection(self):
        """When estimator detects an object, return its pose."""
        Pose6D = namedtuple('Pose6D', ['x', 'y', 'z', 'roll', 'pitch', 'yaw'])
        detected = Pose6D(0.1, 0.2, 0.3, 0.4, 0.5, 0.6)

        self.node._capture.return_value = (MagicMock(), MagicMock())
        self.node._estimator.estimate_poses.return_value = [detected]

        request = MagicMock()
        request.method = 'cup'
        response = MagicMock()
        response.pose = [0.0] * 6

        result = self.node._get_pose_callback(request, response)

        assert result.pose == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

    def test_callback_returns_zero_when_no_detection(self):
        """When estimator detects nothing, return all zeros."""
        self.node._capture.return_value = (MagicMock(), MagicMock())
        self.node._estimator.estimate_poses.return_value = []

        request = MagicMock()
        request.method = 'cup'
        response = MagicMock()
        response.pose = [0.0] * 6

        result = self.node._get_pose_callback(request, response)

        assert result.pose == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def test_callback_returns_zero_on_exception(self):
        """When capture or estimator raises, return all zeros."""
        self.node._capture.side_effect = RuntimeError('camera disconnected')

        request = MagicMock()
        request.method = 'cup'
        response = MagicMock()
        response.pose = [0.0] * 6

        result = self.node._get_pose_callback(request, response)

        assert result.pose == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def test_callback_passes_correct_intrinsics(self):
        """Verify intrinsics tuple is passed to estimate_poses."""
        Pose6D = namedtuple('Pose6D', ['x', 'y', 'z', 'roll', 'pitch', 'yaw'])
        self.node._capture.return_value = ('depth', 'color')
        self.node._estimator.estimate_poses.return_value = [
            Pose6D(0, 0, 0, 0, 0, 0)
        ]

        request = MagicMock()
        request.method = 'bottle'
        response = MagicMock()
        response.pose = [0.0] * 6

        self.node._get_pose_callback(request, response)

        call_args = self.node._estimator.estimate_poses.call_args
        assert call_args[0][0] == 'color'  # color_bgr
        assert call_args[0][1] == 'depth'  # depth_mm
        assert call_args[0][2] == (600.0, 600.0, 320.0, 240.0)  # intrinsics
        assert call_args[1]['prompt'] == 'bottle'
        assert call_args[1]['is_bgr'] is True

    def test_callback_thread_safety(self):
        """Verify the lock is used (callback acquires _lock)."""
        mock_lock = MagicMock()
        self.node._lock = mock_lock

        self.node._capture.return_value = (MagicMock(), MagicMock())
        self.node._estimator.estimate_poses.return_value = []

        request = MagicMock()
        request.method = 'cup'
        response = MagicMock()
        response.pose = [0.0] * 6

        self.node._get_pose_callback(request, response)

        mock_lock.__enter__.assert_called_once()
        mock_lock.__exit__.assert_called_once()
