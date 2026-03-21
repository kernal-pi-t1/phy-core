"""Unit tests for PoseActionServer (action_node)."""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock

import rclpy
from rclpy.node import Node
from rclpy.action import GoalResponse, CancelResponse


class TestPoseActionServerInit(unittest.TestCase):
    """Test PoseActionServer initialization and parameter handling."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def _make_node(self, params=None):
        """Create PoseActionServer with mocked service clients."""
        default_params = {
            'namespace': 'dsr01',
            'frame': 'base',
            'default_vel': 100.0,
            'default_acc': 100.0,
        }
        if params:
            default_params.update(params)

        with patch.object(
            Node, 'create_client'
        ) as mock_create_client, patch(
            'rclpy.action.ActionServer.__init__', return_value=None
        ):
            mock_client = MagicMock()
            mock_client.wait_for_service.return_value = True
            mock_create_client.return_value = mock_client

            from phy_core.node.action_node import PoseActionServer

            # Override default params via ROS parameter overrides
            param_overrides = [
                rclpy.parameter.Parameter(k, value=v)
                for k, v in default_params.items()
            ]
            node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(node, 'pose_action_server',
                          parameter_overrides=param_overrides)

            # Declare and read params as the real __init__ does
            for k, v in default_params.items():
                try:
                    node.declare_parameter(k, v)
                except rclpy.exceptions.ParameterAlreadyDeclaredException:
                    pass

            node.namespace_param = node.get_parameter('namespace').value
            node.frame = node.get_parameter('frame').value
            node.default_vel = float(node.get_parameter('default_vel').value)
            node.default_acc = float(node.get_parameter('default_acc').value)

            # Assign mocked clients
            node.move_line_client = MagicMock()
            node.get_posx_client = MagicMock()
            node.gripper_open_client = MagicMock()
            node.gripper_close_client = MagicMock()

        return node

    def test_node_name(self):
        node = self._make_node()
        assert node.get_name() == 'pose_action_server'
        node.destroy_node()

    def test_default_parameters(self):
        node = self._make_node()
        assert node.frame == 'base'
        assert node.default_vel == 100.0
        assert node.default_acc == 100.0
        node.destroy_node()

    def test_tool_frame_parameter(self):
        node = self._make_node({'frame': 'tool'})
        assert node.frame == 'tool'
        node.destroy_node()

    def test_custom_velocity(self):
        node = self._make_node({'default_vel': 200.0, 'default_acc': 150.0})
        assert node.default_vel == 200.0
        assert node.default_acc == 150.0
        node.destroy_node()


class TestGoalCallback(unittest.TestCase):
    """Test goal_callback accept/reject logic."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.default_vel = 100.0
            self.node.default_acc = 100.0

    def tearDown(self):
        self.node.destroy_node()

    def test_accept_valid_6_element_pose(self):
        goal_request = MagicMock()
        goal_request.target_pose = [1.0, 2.0, 3.0, 0.0, 180.0, 0.0]
        goal_request.method = 'ik'
        assert self.node.goal_callback(goal_request) == GoalResponse.ACCEPT

    def test_accept_fk_method(self):
        goal_request = MagicMock()
        goal_request.target_pose = [0.0, 0.0, 90.0, 0.0, 90.0, 0.0]
        goal_request.method = 'fk'
        assert self.node.goal_callback(goal_request) == GoalResponse.ACCEPT

    def test_accept_empty_method_defaults_to_ik(self):
        goal_request = MagicMock()
        goal_request.target_pose = [1.0, 2.0, 3.0, 0.0, 180.0, 0.0]
        goal_request.method = ''
        assert self.node.goal_callback(goal_request) == GoalResponse.ACCEPT

    def test_reject_invalid_method(self):
        goal_request = MagicMock()
        goal_request.target_pose = [1.0, 2.0, 3.0, 0.0, 180.0, 0.0]
        goal_request.method = 'invalid'
        assert self.node.goal_callback(goal_request) == GoalResponse.REJECT

    def test_reject_5_element_pose(self):
        goal_request = MagicMock()
        goal_request.target_pose = [1.0, 2.0, 3.0, 0.0, 180.0]
        goal_request.method = 'ik'
        assert self.node.goal_callback(goal_request) == GoalResponse.REJECT

    def test_reject_empty_pose(self):
        goal_request = MagicMock()
        goal_request.target_pose = []
        goal_request.method = 'ik'
        assert self.node.goal_callback(goal_request) == GoalResponse.REJECT

    def test_reject_7_element_pose(self):
        goal_request = MagicMock()
        goal_request.target_pose = [1.0, 2.0, 3.0, 0.0, 180.0, 0.0, 99.0]
        goal_request.method = 'ik'
        assert self.node.goal_callback(goal_request) == GoalResponse.REJECT


class TestCancelCallback(unittest.TestCase):
    """Test cancel_callback."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'

    def tearDown(self):
        self.node.destroy_node()

    def test_cancel_accepted(self):
        goal_handle = MagicMock()
        assert self.node.cancel_callback(goal_handle) == CancelResponse.ACCEPT


class TestGetCurrentPose(unittest.TestCase):
    """Test get_current_pose helper."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.default_vel = 100.0
            self.node.default_acc = 100.0
            self.node.get_posx_client = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_returns_pose_on_success(self):
        """When service returns valid data, return 6-element list."""
        import asyncio

        task_pos = MagicMock()
        task_pos.data = [100.0, 200.0, 300.0, 0.0, 180.0, 0.0, 0, 0]

        resp = MagicMock()
        resp.success = True
        resp.task_pos_info = [task_pos]

        self.node.get_posx_client.wait_for_service.return_value = True
        self.node.get_posx_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.get_current_pose())

        assert result == [100.0, 200.0, 300.0, 0.0, 180.0, 0.0]

    def test_returns_none_when_service_unavailable(self):
        """When service is not available, return None."""
        import asyncio

        self.node.get_posx_client.wait_for_service.return_value = False

        result = asyncio.get_event_loop().run_until_complete(
            self.node.get_current_pose())

        assert result is None

    def test_returns_none_on_empty_response(self):
        """When response has no task_pos_info, return None."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        resp.task_pos_info = []

        self.node.get_posx_client.wait_for_service.return_value = True
        self.node.get_posx_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.get_current_pose())

        assert result is None

    def test_returns_none_on_exception(self):
        """When call_async raises, return None."""
        import asyncio

        self.node.get_posx_client.wait_for_service.return_value = True
        self.node.get_posx_client.call_async = AsyncMock(
            side_effect=RuntimeError('connection lost'))

        result = asyncio.get_event_loop().run_until_complete(
            self.node.get_current_pose())

        assert result is None


class TestCallMoveLine(unittest.TestCase):
    """Test call_move_line helper."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.default_vel = 100.0
            self.node.default_acc = 100.0
            self.node.move_line_client = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_move_line_success(self):
        """When MoveLine returns success=True, return True."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line([500.0, 0.0, 400.0, 0.0, 180.0, 0.0]))

        assert result is True

    def test_move_line_failure(self):
        """When MoveLine returns success=False, return False."""
        import asyncio

        resp = MagicMock()
        resp.success = False
        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line([500.0, 0.0, 400.0, 0.0, 180.0, 0.0]))

        assert result is False

    def test_move_line_service_unavailable(self):
        """When service is not available, return False."""
        import asyncio

        self.node.move_line_client.wait_for_service.return_value = False

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line([500.0, 0.0, 400.0, 0.0, 180.0, 0.0]))

        assert result is False

    def test_move_line_exception(self):
        """When call_async raises, return False."""
        import asyncio

        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(
            side_effect=RuntimeError('comm error'))

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line([500.0, 0.0, 400.0, 0.0, 180.0, 0.0]))

        assert result is False

    def test_move_line_base_frame_params(self):
        """Verify correct ref/mode for base frame absolute move."""
        import asyncio
        from phy_core.node.action_node import DR_BASE

        resp = MagicMock()
        resp.success = True
        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(return_value=resp)

        asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line(
                [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], ref=DR_BASE, mode=0))

        req = self.node.move_line_client.call_async.call_args[0][0]
        assert req.ref == DR_BASE
        assert req.mode == 0

    def test_move_line_tool_frame_params(self):
        """Verify correct ref/mode for tool frame relative move."""
        import asyncio
        from phy_core.node.action_node import DR_TOOL

        resp = MagicMock()
        resp.success = True
        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(return_value=resp)

        asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line(
                [0.0, 0.0, 10.0, 0.0, 0.0, 0.0], ref=DR_TOOL, mode=1))

        req = self.node.move_line_client.call_async.call_args[0][0]
        assert req.ref == DR_TOOL
        assert req.mode == 1

    def test_move_line_velocity_params(self):
        """Verify velocity and acceleration are set correctly."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        self.node.move_line_client.wait_for_service.return_value = True
        self.node.move_line_client.call_async = AsyncMock(return_value=resp)
        self.node.default_vel = 200.0
        self.node.default_acc = 150.0

        asyncio.get_event_loop().run_until_complete(
            self.node.call_move_line([0.0] * 6))

        req = self.node.move_line_client.call_async.call_args[0][0]
        assert list(req.vel) == [200.0, 30.0]
        assert list(req.acc) == [150.0, 30.0]


class TestControlGripper(unittest.TestCase):
    """Test control_gripper helper."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.gripper_open_client = MagicMock()
            self.node.gripper_close_client = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_grip_close_success(self):
        """grip=True calls close client and returns True."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        resp.message = 'closed'
        self.node.gripper_close_client.wait_for_service.return_value = True
        self.node.gripper_close_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.control_gripper(True))

        assert result is True
        self.node.gripper_close_client.call_async.assert_called_once()

    def test_grip_open_success(self):
        """grip=False calls open client and returns True."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        resp.message = 'opened'
        self.node.gripper_open_client.wait_for_service.return_value = True
        self.node.gripper_open_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.control_gripper(False))

        assert result is True
        self.node.gripper_open_client.call_async.assert_called_once()

    def test_grip_service_unavailable(self):
        """When gripper service not available, return False."""
        import asyncio

        self.node.gripper_close_client.wait_for_service.return_value = False

        result = asyncio.get_event_loop().run_until_complete(
            self.node.control_gripper(True))

        assert result is False

    def test_grip_failure_response(self):
        """When gripper returns success=False, return False."""
        import asyncio

        resp = MagicMock()
        resp.success = False
        resp.message = 'jammed'
        self.node.gripper_close_client.wait_for_service.return_value = True
        self.node.gripper_close_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.control_gripper(True))

        assert result is False

    def test_grip_exception(self):
        """When call_async raises, return False."""
        import asyncio

        self.node.gripper_close_client.wait_for_service.return_value = True
        self.node.gripper_close_client.call_async = AsyncMock(
            side_effect=RuntimeError('gripper error'))

        result = asyncio.get_event_loop().run_until_complete(
            self.node.control_gripper(True))

        assert result is False


class TestExecuteCallback(unittest.TestCase):
    """Test execute_callback full flow."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.default_vel = 100.0
            self.node.default_acc = 100.0
            self.node.move_line_client = MagicMock()
            self.node.get_posx_client = MagicMock()
            self.node.gripper_open_client = MagicMock()
            self.node.gripper_close_client = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def _make_goal_handle(self, pose, grip, method='ik'):
        goal_handle = MagicMock()
        goal_handle.request.target_pose = pose
        goal_handle.request.grip = grip
        goal_handle.request.method = method
        return goal_handle

    def test_base_frame_move_and_grip_success(self):
        """Full success: base frame IK move + gripper close."""
        import asyncio
        from phy_core.node.action_node import DR_BASE

        self.node.get_current_pose = AsyncMock(
            return_value=[100.0, 0.0, 300.0, 0.0, 180.0, 0.0])
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=True)

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], True, method='ik')

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is True
        goal_handle.succeed.assert_called_once()
        self.node.call_move_line.assert_called_once_with(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], ref=DR_BASE, mode=0)
        self.node.control_gripper.assert_called_once_with(True)

    def test_tool_frame_relative_move(self):
        """Tool frame uses ref=DR_TOOL and mode=1."""
        import asyncio
        from phy_core.node.action_node import DR_TOOL

        self.node.frame = 'tool'
        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=True)

        goal_handle = self._make_goal_handle(
            [0.0, 0.0, 10.0, 0.0, 0.0, 0.0], False, method='ik')

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is True
        self.node.call_move_line.assert_called_once_with(
            [0.0, 0.0, 10.0, 0.0, 0.0, 0.0], ref=DR_TOOL, mode=1)
        self.node.control_gripper.assert_called_once_with(False)

    def test_fk_mode_calls_move_joint(self):
        """FK mode calls call_move_joint instead of call_move_line."""
        import asyncio

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_joint = AsyncMock(return_value=True)
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=True)

        joints = [0.0, 0.0, 90.0, 0.0, 90.0, 0.0]
        goal_handle = self._make_goal_handle(joints, False, method='fk')

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is True
        self.node.call_move_joint.assert_called_once_with(joints)
        self.node.call_move_line.assert_not_called()

    def test_fk_mode_failure_aborts(self):
        """FK mode aborts when MoveJoint fails."""
        import asyncio

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_joint = AsyncMock(return_value=False)
        self.node.control_gripper = AsyncMock(return_value=True)

        goal_handle = self._make_goal_handle(
            [0.0, 0.0, 90.0, 0.0, 90.0, 0.0], True, method='fk')

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is False
        goal_handle.abort.assert_called_once()

    def test_empty_method_defaults_to_ik(self):
        """Empty method string defaults to IK (MoveLine)."""
        import asyncio
        from phy_core.node.action_node import DR_BASE

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.call_move_joint = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=True)

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], False, method='')

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is True
        self.node.call_move_line.assert_called_once()
        self.node.call_move_joint.assert_not_called()

    def test_move_failure_aborts(self):
        """When MoveLine fails, goal is aborted."""
        import asyncio

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_line = AsyncMock(return_value=False)

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], True)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is False
        goal_handle.abort.assert_called_once()
        goal_handle.succeed.assert_not_called()

    def test_gripper_failure_still_succeeds(self):
        """When gripper fails but move succeeds, overall success=True."""
        import asyncio

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=False)

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], True)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is True
        goal_handle.succeed.assert_called_once()

    def test_exception_aborts(self):
        """When an exception occurs, goal is aborted."""
        import asyncio

        self.node.get_current_pose = AsyncMock(
            side_effect=RuntimeError('unexpected'))

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], True)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        assert result.success is False
        goal_handle.abort.assert_called_once()

    def test_feedback_published(self):
        """Verify feedback is published during execution."""
        import asyncio

        self.node.get_current_pose = AsyncMock(return_value=None)
        self.node.call_move_line = AsyncMock(return_value=True)
        self.node.control_gripper = AsyncMock(return_value=True)

        goal_handle = self._make_goal_handle(
            [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], True)

        asyncio.get_event_loop().run_until_complete(
            self.node.execute_callback(goal_handle))

        # At least 3 feedback calls: current pose query, move, gripper
        assert goal_handle.publish_feedback.call_count >= 3


class TestCallMoveJoint(unittest.TestCase):
    """Test call_move_joint helper (FK)."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from phy_core.node.action_node import PoseActionServer
        with patch.object(Node, 'create_client'), \
             patch('rclpy.action.ActionServer.__init__', return_value=None):
            self.node = PoseActionServer.__new__(PoseActionServer)
            Node.__init__(self.node, 'pose_action_server')
            self.node.declare_parameter('namespace', 'dsr01')
            self.node.declare_parameter('frame', 'base')
            self.node.declare_parameter('default_vel', 100.0)
            self.node.declare_parameter('default_acc', 100.0)
            self.node.namespace = 'dsr01'
            self.node.frame = 'base'
            self.node.default_vel = 100.0
            self.node.default_acc = 100.0
            self.node.move_joint_client = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_move_joint_success(self):
        """When MoveJoint returns success=True, return True."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        self.node.move_joint_client.wait_for_service.return_value = True
        self.node.move_joint_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_joint([0.0, 0.0, 90.0, 0.0, 90.0, 0.0]))

        assert result is True

    def test_move_joint_failure(self):
        """When MoveJoint returns success=False, return False."""
        import asyncio

        resp = MagicMock()
        resp.success = False
        self.node.move_joint_client.wait_for_service.return_value = True
        self.node.move_joint_client.call_async = AsyncMock(return_value=resp)

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_joint([0.0, 0.0, 90.0, 0.0, 90.0, 0.0]))

        assert result is False

    def test_move_joint_service_unavailable(self):
        """When service is not available, return False."""
        import asyncio

        self.node.move_joint_client.wait_for_service.return_value = False

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_joint([0.0, 0.0, 90.0, 0.0, 90.0, 0.0]))

        assert result is False

    def test_move_joint_exception(self):
        """When call_async raises, return False."""
        import asyncio

        self.node.move_joint_client.wait_for_service.return_value = True
        self.node.move_joint_client.call_async = AsyncMock(
            side_effect=RuntimeError('joint error'))

        result = asyncio.get_event_loop().run_until_complete(
            self.node.call_move_joint([0.0, 0.0, 90.0, 0.0, 90.0, 0.0]))

        assert result is False

    def test_move_joint_request_params(self):
        """Verify MoveJoint request fields are set correctly."""
        import asyncio

        resp = MagicMock()
        resp.success = True
        self.node.move_joint_client.wait_for_service.return_value = True
        self.node.move_joint_client.call_async = AsyncMock(return_value=resp)

        joints = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        asyncio.get_event_loop().run_until_complete(
            self.node.call_move_joint(joints))

        req = self.node.move_joint_client.call_async.call_args[0][0]
        assert list(req.pos) == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        assert req.vel == 60.0
        assert req.acc == 60.0
        assert req.mode == 0
        assert req.sync_type == 0
