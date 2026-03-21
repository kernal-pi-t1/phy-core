"""Unit tests for OrchestrationNode."""

import math
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

import numpy as np
import rclpy
from rclpy.node import Node

from phy_interface.srv import Json, GetPose
from phy_interface.action import Move


class TestOrchestrationNodeConstants(unittest.TestCase):
    """Test constants and class attributes without spinning up ROS."""

    def test_state_constants_defined(self):
        from phy_core.node.phy_core_node import OrchestrationNode

        assert OrchestrationNode.STATE_IDLE == 'IDLE'
        assert OrchestrationNode.STATE_INIT_POSE == 'INIT_POSE'
        assert OrchestrationNode.STATE_GET_PICK_POSE == 'GET_PICK_POSE'
        assert OrchestrationNode.STATE_PICK_EXECUTE == 'PICK_EXECUTE'
        assert OrchestrationNode.STATE_VAL_POSE == 'VAL_POSE'
        assert OrchestrationNode.STATE_VALIDATE == 'VALIDATE'
        assert OrchestrationNode.STATE_PLACE_POSE == 'PLACE_POSE'
        assert OrchestrationNode.STATE_PLACE_RETURN == 'PLACE_RETURN'

    def test_zero_pose(self):
        from phy_core.node.phy_core_node import _ZERO_POSE

        assert _ZERO_POSE == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        assert len(_ZERO_POSE) == 6


class TestOrchestrationNodeInit(unittest.TestCase):
    """Test OrchestrationNode initialization and parameter loading."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        """Create node with mocked external dependencies."""
        self.mock_pose = [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]

        # Patch wait_for_service and wait_for_server to skip blocking
        with patch.object(
            rclpy.node.Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionClient.__init__', return_value=None
        ), patch(
            'rclpy.action.ActionClient.wait_for_server', return_value=True
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.phy_core_node import OrchestrationNode

            self.node = OrchestrationNode()

    def tearDown(self):
        self.node.destroy_node()

    def test_node_name(self):
        assert self.node.get_name() == 'orchestration_node'

    def test_initial_state_idle(self):
        assert self.node._state == 'IDLE'

    def test_parameters_declared(self):
        param_names = [p.name for p in self.node.get_parameters(
            ['init_pose', 'val_pose', 'place_pose', 'place_return_pose']
        )]
        assert 'init_pose' in param_names
        assert 'val_pose' in param_names
        assert 'place_pose' in param_names
        assert 'place_return_pose' in param_names

    def test_default_poses_are_zero(self):
        from phy_core.node.phy_core_node import _ZERO_POSE

        assert self.node.init_pose == _ZERO_POSE
        assert self.node.val_pose == _ZERO_POSE
        assert self.node.place_pose == _ZERO_POSE
        assert self.node.place_return_pose == _ZERO_POSE

    def test_load_pose_param_validates_length(self):
        """_load_pose_param should raise ValueError for non-6-element param."""
        self.node.declare_parameter('bad_pose', [1.0, 2.0])
        with self.assertRaises(ValueError):
            self.node._load_pose_param('bad_pose')


class TestOrchestrationNodeCallGetPose(unittest.TestCase):
    """Test _call_get_pose helper."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        with patch.object(
            rclpy.node.Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionClient.__init__', return_value=None
        ), patch(
            'rclpy.action.ActionClient.wait_for_server', return_value=True
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.phy_core_node import OrchestrationNode

            self.node = OrchestrationNode()

    def tearDown(self):
        self.node.destroy_node()

    @patch('rclpy.spin_until_future_complete')
    def test_call_get_pose_returns_pose(self, mock_spin):
        """When sam3 returns a valid pose, _call_get_pose returns it."""
        expected_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        mock_result = MagicMock()
        mock_result.pose = expected_pose

        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        result, count = self.node._call_get_pose('test_object')
        assert result == expected_pose

    @patch('rclpy.spin_until_future_complete')
    def test_call_get_pose_returns_none_for_zero(self, mock_spin):
        """When sam3 returns zero pose, _call_get_pose returns None."""
        mock_result = MagicMock()
        mock_result.pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        result, count = self.node._call_get_pose('test_object')
        assert result is None


class TestOrchestrationNodeSendMove(unittest.TestCase):
    """Test _send_move helper."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        with patch.object(
            rclpy.node.Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionClient.__init__', return_value=None
        ), patch(
            'rclpy.action.ActionClient.wait_for_server', return_value=True
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.phy_core_node import OrchestrationNode

            self.node = OrchestrationNode()

    def tearDown(self):
        self.node.destroy_node()

    @patch('rclpy.spin_until_future_complete')
    def test_send_move_success(self, mock_spin):
        """_send_move returns True when action succeeds."""
        mock_goal_handle = MagicMock()
        mock_goal_handle.accepted = True

        mock_result_wrapper = MagicMock()
        mock_result_wrapper.result.success = True

        mock_result_future = MagicMock()
        mock_result_future.result.return_value = mock_result_wrapper

        mock_goal_handle.get_result_async.return_value = mock_result_future

        mock_send_future = MagicMock()
        mock_send_future.result.return_value = mock_goal_handle

        self.node._robot_client = MagicMock()
        self.node._robot_client.send_goal_async.return_value = mock_send_future

        pose = [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]
        result = self.node._send_move(pose, 'TEST')
        assert result is True

    @patch('rclpy.spin_until_future_complete')
    def test_send_move_rejected(self, mock_spin):
        """_send_move returns False when goal is rejected."""
        mock_goal_handle = MagicMock()
        mock_goal_handle.accepted = False

        mock_send_future = MagicMock()
        mock_send_future.result.return_value = mock_goal_handle

        self.node._robot_client = MagicMock()
        self.node._robot_client.send_goal_async.return_value = mock_send_future

        pose = [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]
        result = self.node._send_move(pose, 'TEST')
        assert result is False


class TestOrchestrationNodeTaskCallback(unittest.TestCase):
    """Test the _task_callback state machine."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        with patch.object(
            rclpy.node.Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionClient.__init__', return_value=None
        ), patch(
            'rclpy.action.ActionClient.wait_for_server', return_value=True
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.phy_core_node import OrchestrationNode

            self.node = OrchestrationNode()

    def tearDown(self):
        self.node.destroy_node()

    def _mock_helpers(self):
        """Mock all helper methods for task callback tests."""
        self.node._send_move = MagicMock(return_value=True)
        self.node._open_gripper = MagicMock()
        self.node._close_gripper = MagicMock()
        self.node._read_gripper_torque = MagicMock(return_value=100)
        self.node._transform_pose = MagicMock(side_effect=lambda p: p)
        self.node._call_count_objects = MagicMock(return_value=0)

        vlm_ok = MagicMock()
        vlm_ok.decision = 'RETURN_APPROVED'
        self.node._call_vlm_judge = MagicMock(return_value=vlm_ok)

    def test_task_success_flow(self):
        """Full success: init->pre_grasp->descend->lift->val->place->return."""
        pick_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self._mock_helpers()
        self.node._call_get_pose = MagicMock(return_value=(pick_pose, 1))

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is True
        assert self.node._state == 'IDLE'
        # init + pre_grasp + descend + lift + recheck_init + val + place + return = 8 moves
        assert self.node._send_move.call_count == 8

    def test_task_fail_object_not_detected(self):
        """Fail when sam3 cannot detect the object."""
        self._mock_helpers()
        self.node._call_get_pose = MagicMock(return_value=(None, 0))

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is False
        assert self.node._state == 'IDLE'

    def test_task_fail_init_move_fails(self):
        """Fail when robot cannot reach init pose."""
        self._mock_helpers()
        self.node._send_move = MagicMock(return_value=False)

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is False
        assert self.node._state == 'IDLE'

    def test_task_fail_torque_too_low(self):
        """Fail when gripper torque indicates empty grasp."""
        pick_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self._mock_helpers()
        self.node._call_get_pose = MagicMock(return_value=(pick_pose, 1))
        self.node._read_gripper_torque = MagicMock(return_value=10)

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is False
        assert self.node._state == 'IDLE'

    def test_task_retry_on_validation_fail(self):
        """When VLM validation fails, retry; succeed on second attempt."""
        pick_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self._mock_helpers()
        self.node._call_get_pose = MagicMock(return_value=(pick_pose, 1))

        vlm_fail = MagicMock()
        vlm_fail.decision = 'REJECTED'
        vlm_ok = MagicMock()
        vlm_ok.decision = 'RETURN_APPROVED'
        self.node._call_vlm_judge = MagicMock(side_effect=[vlm_fail, vlm_ok])

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is True
        assert self.node._state == 'IDLE'
        # Retry 1: init+pre_grasp+descend+lift+recheck_init+val+place_return = 7
        # Retry 2: init+pre_grasp+descend+lift+recheck_init+val+place+return = 8
        # Total = 15
        assert self.node._send_move.call_count == 15


class TestDetectAndTransform(unittest.TestCase):
    """Test object detection → camera-to-base coordinate transform pipeline."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        with patch.object(
            rclpy.node.Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionClient.__init__', return_value=None
        ), patch(
            'rclpy.action.ActionClient.wait_for_server', return_value=True
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.phy_core_node import OrchestrationNode
            self.node = OrchestrationNode()

    def tearDown(self):
        self.node.destroy_node()

    # ------------------------------------------------------------------
    # _transform_pose unit tests
    # ------------------------------------------------------------------
    def test_transform_identity_rotation(self):
        """camera_rpy=0 → base = cam_pos + offset, orientation unchanged."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 0.0])

        cam_pose = [0.1, 0.05, 0.5, 0.0, 0.0, 0.0]
        result = self.node._transform_pose(cam_pose)

        # position = (cam + offset) * 1000 (mm)
        np.testing.assert_allclose(result[0], (0.1 + 0.80) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[1], (0.05 + 0.0) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[2], (0.5 + 0.66) * 1000, atol=1e-3)
        # orientation unchanged (deg)
        np.testing.assert_allclose(result[3:], [0.0, 0.0, 0.0], atol=1e-3)

    def test_transform_with_camera_yaw_90(self):
        """camera yaw=90° rotates X→Y, Y→-X in base frame."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 90.0])

        cam_pose = [0.1, 0.0, 0.5, 0.0, 0.0, 0.0]
        result = self.node._transform_pose(cam_pose)

        # R_yaw90 @ [0.1, 0, 0.5] = [0, 0.1, 0.5] + offset, in mm
        np.testing.assert_allclose(result[0], (0.0 + 0.80) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[1], (0.1 + 0.0) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[2], (0.5 + 0.66) * 1000, atol=1e-3)

    def test_transform_preserves_6dof(self):
        """Result always has 6 float elements."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 0.0])

        cam_pose = [0.3, -0.1, 0.4, 0.1, -0.2, 0.3]
        result = self.node._transform_pose(cam_pose)

        assert len(result) == 6
        assert all(isinstance(v, float) for v in result)

    def test_transform_negative_camera_coords(self):
        """Negative camera coordinates transform correctly."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 0.0])

        cam_pose = [-0.1, -0.2, 0.3, 0.0, 0.0, 0.0]
        result = self.node._transform_pose(cam_pose)

        np.testing.assert_allclose(result[0], (-0.1 + 0.80) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[1], (-0.2 + 0.0) * 1000, atol=1e-3)
        np.testing.assert_allclose(result[2], (0.3 + 0.66) * 1000, atol=1e-3)

    # ------------------------------------------------------------------
    # detect → transform end-to-end
    # ------------------------------------------------------------------
    @patch('rclpy.spin_until_future_complete')
    def test_detect_then_transform_pipeline(self, mock_spin):
        """Full pipeline: get_pose returns camera pose → _transform_pose → base coords."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 0.0])

        cam_pose = [0.15, -0.05, 0.40, 0.0, 0.0, 0.0]

        mock_result = MagicMock()
        mock_result.pose = cam_pose
        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        # Step 1: detect
        detected, count = self.node._call_get_pose('test_object')
        assert detected == cam_pose

        # Step 2: transform
        base_pose = self.node._transform_pose(detected)

        np.testing.assert_allclose(base_pose[0], (0.15 + 0.80) * 1000, atol=1e-3)
        np.testing.assert_allclose(base_pose[1], (-0.05 + 0.0) * 1000, atol=1e-3)
        np.testing.assert_allclose(base_pose[2], (0.40 + 0.66) * 1000, atol=1e-3)

    @patch('rclpy.spin_until_future_complete')
    def test_detect_failure_returns_none(self, mock_spin):
        """When object not detected (zero pose), pipeline stops early."""
        mock_result = MagicMock()
        mock_result.pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        detected, count = self.node._call_get_pose('nonexistent_object')
        assert detected is None

    @patch('rclpy.spin_until_future_complete')
    def test_detect_transform_with_rotated_camera(self, mock_spin):
        """Detect + transform with non-zero camera RPY."""
        from phy_core.transform import CameraToBaseTransform
        self.node._cam_to_base = CameraToBaseTransform([0.80, 0.0, 0.66], [0.0, 0.0, 90.0])

        cam_pose = [0.2, 0.0, 0.5, 0.0, 0.0, 0.0]

        mock_result = MagicMock()
        mock_result.pose = cam_pose
        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        detected, count = self.node._call_get_pose('cup')
        base_pose = self.node._transform_pose(detected)

        # yaw 90°: X_cam→Y_base, Y_cam→-X_base, in mm
        np.testing.assert_allclose(base_pose[0], (0.0 + 0.80) * 1000, atol=1e-3)
        np.testing.assert_allclose(base_pose[1], (0.2 + 0.0) * 1000, atol=1e-3)
        np.testing.assert_allclose(base_pose[2], (0.5 + 0.66) * 1000, atol=1e-3)
