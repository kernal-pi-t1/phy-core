"""Pick-and-place orchestration node.

State machine that coordinates robot_node (action server) and sam3_node
(perception services) for pick-validate-place cycles.

Receives JSON prompts via PickPlaceTask service, orchestrates the full cycle:
init_pose → get_pick_pose → pick → val_pose → validate → place/retry

Threading model:
    - MultiThreadedExecutor with dual callback groups
    - MutuallyExclusiveCallbackGroup for service server (one task at a time)
    - ReentrantCallbackGroup for outbound clients (no deadlock)
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient

from pick_place_interfaces.srv import PickPlaceTask, GetPickPose, ValidateObject
from pick_place_interfaces.msg import ObjectPose

# NOTE: Import the actual robot action type here after Step 0 discovery.
# Example: from robot_interfaces.action import MoveToPose
# For now, we use a placeholder that must be replaced.
_ROBOT_ACTION_TYPE = None  # Replace with actual action type
_ROBOT_ACTION_NAME = '/robot/move_to_pose'  # Replace with actual action name


class OrchestrationNode(Node):
    """State machine orchestrating pick-validate-place cycles."""

    # State constants
    STATE_IDLE = 'IDLE'
    STATE_INIT_POSE = 'INIT_POSE'
    STATE_GET_PICK_POSE = 'GET_PICK_POSE'
    STATE_PICK_POSE = 'PICK_POSE'
    STATE_VAL_POSE = 'VAL_POSE'
    STATE_VALIDATE = 'VALIDATE'
    STATE_PLACE_POSE = 'PLACE_POSE'
    STATE_PLACE_RETURN = 'PLACE_RETURN'

    def __init__(self):
        super().__init__('orchestration_node')

        # --- Callback groups ---
        # MutuallyExclusive for task service: one pick-place cycle at a time
        self._task_cb_group = MutuallyExclusiveCallbackGroup()
        # Reentrant for outbound clients: allows blocking calls inside service callback
        self._client_cb_group = ReentrantCallbackGroup()

        # --- Declare waypoint parameters ---
        self.declare_parameter('init_pose', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter('val_pose', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter('place_pose', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter('place_return_pose', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Load fixed waypoints from parameters
        self.init_pose = self._load_pose_param('init_pose')
        self.val_pose = self._load_pose_param('val_pose')
        self.place_pose = self._load_pose_param('place_pose')
        self.place_return_pose = self._load_pose_param('place_return_pose')

        # --- Service server (entry point) ---
        self._task_service = self.create_service(
            PickPlaceTask, 'pick_place_task',
            self._task_callback,
            callback_group=self._task_cb_group
        )

        # --- Service clients (sam3_node) ---
        self._get_pose_client = self.create_client(
            GetPickPose, 'get_pick_pose',
            callback_group=self._client_cb_group
        )
        self._validate_client = self.create_client(
            ValidateObject, 'validate_object',
            callback_group=self._client_cb_group
        )

        # --- Action client (robot_node) ---
        # NOTE: Uncomment and configure after Step 0 discovery:
        # self._robot_client = ActionClient(
        #     self, _ROBOT_ACTION_TYPE, _ROBOT_ACTION_NAME,
        #     callback_group=self._client_cb_group
        # )

        # --- Wait for sam3_node services ---
        self.get_logger().info('Waiting for sam3_node services...')
        if not self._get_pose_client.wait_for_service(timeout_sec=120.0):
            self.get_logger().error('get_pick_pose service not available after 120s')
            raise RuntimeError('sam3_node get_pick_pose service not available')
        if not self._validate_client.wait_for_service(timeout_sec=120.0):
            self.get_logger().error('validate_object service not available after 120s')
            raise RuntimeError('sam3_node validate_object service not available')

        self.get_logger().info('orchestration_node ready. Service: pick_place_task')
        self._state = self.STATE_IDLE

    def _load_pose_param(self, name):
        """Load a 6-element pose parameter as ObjectPose msg."""
        values = self.get_parameter(name).get_parameter_value().double_array_value
        if len(values) != 6:
            raise ValueError(
                f"Parameter '{name}' must have 6 elements [x,y,z,r,p,y], got {len(values)}"
            )
        pose = ObjectPose()
        pose.x, pose.y, pose.z = values[0], values[1], values[2]
        pose.roll, pose.pitch, pose.yaw = values[3], values[4], values[5]
        self.get_logger().info(
            f"Loaded {name}: [{values[0]:.3f}, {values[1]:.3f}, {values[2]:.3f}, "
            f"{values[3]:.2f}, {values[4]:.2f}, {values[5]:.2f}]"
        )
        return pose

    # ------------------------------------------------------------------
    # Robot action helper
    # ------------------------------------------------------------------

    def _send_robot_action(self, pose, action_name=''):
        """Send a pose goal to robot_node and wait for result.

        NOTE: This is a placeholder. Replace with actual ActionClient call
        after discovering robot_node's action type in Step 0.

        Args:
            pose: ObjectPose msg with target position.
            action_name: Human-readable name for logging.

        Returns:
            Object with .success attribute (bool).
        """
        self.get_logger().info(
            f'[{action_name}] Sending robot action: '
            f'x={pose.x:.4f} y={pose.y:.4f} z={pose.z:.4f} '
            f'r={pose.roll:.2f} p={pose.pitch:.2f} y={pose.yaw:.2f}'
        )

        # TODO: Replace this placeholder with actual robot action call:
        #
        # goal = _ROBOT_ACTION_TYPE.Goal()
        # goal.target_pose = pose  # Map fields to actual goal type
        # future = self._robot_client.send_goal_async(goal)
        # rclpy.spin_until_future_complete(self, future)
        # goal_handle = future.result()
        # if not goal_handle.accepted:
        #     return _ActionResult(success=False)
        # result_future = goal_handle.get_result_async()
        # rclpy.spin_until_future_complete(self, result_future)
        # return result_future.result().result

        # Placeholder: simulate success
        class _PlaceholderResult:
            success = True
        self.get_logger().warn(
            f'[{action_name}] Using placeholder robot action (always succeeds). '
            'Replace with actual ActionClient after Step 0 discovery.'
        )
        return _PlaceholderResult()

    # ------------------------------------------------------------------
    # Service client helpers
    # ------------------------------------------------------------------

    def _call_get_pick_pose(self, object_name):
        """Call sam3_node get_pick_pose service synchronously."""
        req = GetPickPose.Request()
        req.object_name = object_name
        future = self._get_pose_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def _call_validate_object(self, object_name):
        """Call sam3_node validate_object service synchronously."""
        req = ValidateObject.Request()
        req.object_name = object_name
        future = self._validate_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    # ------------------------------------------------------------------
    # Main state machine
    # ------------------------------------------------------------------

    def _task_callback(self, request, response):
        """Execute pick-validate-place cycle for the given object.

        State machine flow:
            init → sam3(get_pose) → pick → val → sam3(validate)
            → true:  place → init → success
            → false: place_return → (loop back to init → retry)
        """
        object_name = request.object_name
        return_reason = request.return_reason
        self.get_logger().info(
            f'=== PickPlaceTask received: object="{object_name}", '
            f'reason="{return_reason}" ==='
        )

        retry_count = 0

        while True:
            # 1. Move to init pose
            self._state = self.STATE_INIT_POSE
            self.get_logger().info(f'[State: INIT_POSE] (retry={retry_count})')
            result = self._send_robot_action(self.init_pose, 'INIT_POSE')
            if not result.success:
                response.success = False
                response.error_message = 'robot_node failed: init_pose'
                self.get_logger().error(response.error_message)
                self._state = self.STATE_IDLE
                return response

            # 2. Get pick pose from sam3
            self._state = self.STATE_GET_PICK_POSE
            self.get_logger().info(f'[State: GET_PICK_POSE] object="{object_name}"')
            pose_resp = self._call_get_pick_pose(object_name)
            if not pose_resp.success:
                response.success = False
                response.error_message = (
                    f'sam3 get_pick_pose failed: {pose_resp.error_message}'
                )
                self.get_logger().error(response.error_message)
                self._state = self.STATE_IDLE
                return response

            # 3. Move to pick pose (dynamic, from sam3)
            self._state = self.STATE_PICK_POSE
            self.get_logger().info('[State: PICK_POSE]')
            result = self._send_robot_action(pose_resp.pose, 'PICK_POSE')
            if not result.success:
                response.success = False
                response.error_message = 'robot_node failed: pick_pose'
                self.get_logger().error(response.error_message)
                self._state = self.STATE_IDLE
                return response

            # 4. Move to validation pose
            self._state = self.STATE_VAL_POSE
            self.get_logger().info('[State: VAL_POSE]')
            result = self._send_robot_action(self.val_pose, 'VAL_POSE')
            if not result.success:
                response.success = False
                response.error_message = 'robot_node failed: val_pose'
                self.get_logger().error(response.error_message)
                self._state = self.STATE_IDLE
                return response

            # 5. Validate object
            self._state = self.STATE_VALIDATE
            self.get_logger().info(f'[State: VALIDATE] object="{object_name}"')
            val_resp = self._call_validate_object(object_name)

            if val_resp.is_valid:
                # 6a. SUCCESS PATH: place object
                self._state = self.STATE_PLACE_POSE
                self.get_logger().info('[State: PLACE_POSE] Validation PASSED')
                result = self._send_robot_action(self.place_pose, 'PLACE_POSE')
                if not result.success:
                    response.success = False
                    response.error_message = 'robot_node failed: place_pose'
                    self.get_logger().error(response.error_message)
                    self._state = self.STATE_IDLE
                    return response

                # Return to init after placing
                self.get_logger().info('[State: INIT_POSE] Returning after place')
                result = self._send_robot_action(self.init_pose, 'RETURN_TO_INIT')
                if not result.success:
                    response.success = False
                    response.error_message = (
                        'robot_node failed: return to init_pose after place'
                    )
                    self.get_logger().error(response.error_message)
                    self._state = self.STATE_IDLE
                    return response

                # Done!
                response.success = True
                response.error_message = ''
                self.get_logger().info(
                    f'=== PickPlaceTask SUCCESS for "{object_name}" '
                    f'(retries={retry_count}) ==='
                )
                self._state = self.STATE_IDLE
                return response
            else:
                # 6b. RETRY PATH: return defective item
                retry_count += 1
                self._state = self.STATE_PLACE_RETURN
                self.get_logger().warn(
                    f'[State: PLACE_RETURN] Validation FAILED for "{object_name}", '
                    f'retry attempt {retry_count}'
                )
                result = self._send_robot_action(
                    self.place_return_pose, 'PLACE_RETURN'
                )
                if not result.success:
                    response.success = False
                    response.error_message = 'robot_node failed: place_return'
                    self.get_logger().error(response.error_message)
                    self._state = self.STATE_IDLE
                    return response
                # Loop continues → init_pose → get_pick_pose → ...


def main(args=None):
    rclpy.init(args=args)
    node = OrchestrationNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
