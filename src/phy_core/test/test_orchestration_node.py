"""Unit tests for OrchestrationNode."""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock

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
        assert OrchestrationNode.STATE_PICK_POSE == 'PICK_POSE'
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

        result = self.node._call_get_pose('test_object')
        assert result == expected_pose

    @patch('rclpy.spin_until_future_complete')
    def test_call_get_pose_returns_none_for_zero(self, mock_spin):
        """When sam3 returns zero pose, _call_get_pose returns None."""
        mock_result = MagicMock()
        mock_result.pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        self.node._get_pose_client.call_async = MagicMock(return_value=mock_future)

        result = self.node._call_get_pose('test_object')
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

    def test_task_success_flow(self):
        """Full success: init->get_pose->pick->val->validate(pass)->place->init."""
        pick_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        val_pose = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        self.node._send_move = MagicMock(return_value=True)
        self.node._call_get_pose = MagicMock(side_effect=[pick_pose, val_pose])

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is True
        assert self.node._state == 'IDLE'
        # init + pick + val + place + return_to_init = 5 moves
        assert self.node._send_move.call_count == 5

    def test_task_fail_object_not_detected(self):
        """Fail when sam3 cannot detect the object."""
        self.node._send_move = MagicMock(return_value=True)
        self.node._call_get_pose = MagicMock(return_value=None)

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is False
        assert self.node._state == 'IDLE'

    def test_task_fail_init_move_fails(self):
        """Fail when robot cannot reach init pose."""
        self.node._send_move = MagicMock(return_value=False)

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is False
        assert self.node._state == 'IDLE'

    def test_task_retry_on_validation_fail(self):
        """When validation fails, retry; succeed on second attempt."""
        pick_pose = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        val_detected = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        # 1st: get_pose ok, validate fail -> retry
        # 2nd: get_pose ok, validate ok -> success
        self.node._call_get_pose = MagicMock(
            side_effect=[pick_pose, None, pick_pose, val_detected]
        )
        self.node._send_move = MagicMock(return_value=True)

        request = MagicMock()
        request.payload = 'cup'
        response = MagicMock()

        result = self.node._task_callback(request, response)

        assert result.success is True
        assert self.node._state == 'IDLE'
        # Retry 1: init+pick+val+place_return = 4
        # Retry 2: init+pick+val+place+return_init = 5
        # Total = 9
        assert self.node._send_move.call_count == 9
