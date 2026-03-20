"""Pick-and-place orchestration node.

State machine that coordinates robot_node (Move action) and sam3_node
(GetPose service) for pick-validate-place cycles.

Receives prompts via Json service, orchestrates the full cycle:
init_pose -> get_pose -> pick -> val_pose -> validate -> place/retry

Interfaces (all from phy_interface):
    Json.srv    : entry point (payload = object name)
    GetPose.srv : sam3 perception (method = object name, pose = float64[6])
    Move.action : robot motion (target_pose = float64[6])

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

from phy_interface.srv import Json, GetPose, VlmJudge
from phy_interface.action import Move

_ZERO_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


class OrchestrationNode(Node):
    """State machine orchestrating pick-validate-place cycles."""

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
        self._task_cb_group = MutuallyExclusiveCallbackGroup()
        self._client_cb_group = ReentrantCallbackGroup()

        # --- Declare waypoint parameters ---
        self.declare_parameter('init_pose', _ZERO_POSE)
        self.declare_parameter('val_pose', _ZERO_POSE)
        self.declare_parameter('place_pose', _ZERO_POSE)
        self.declare_parameter('place_return_pose', _ZERO_POSE)

        # Load fixed waypoints as float64[6] lists
        self.init_pose = self._load_pose_param('init_pose')
        self.val_pose = self._load_pose_param('val_pose')
        self.place_pose = self._load_pose_param('place_pose')
        self.place_return_pose = self._load_pose_param('place_return_pose')

        # --- Service server (entry point) ---
        self._task_service = self.create_service(
            Json, 'pick_place_task',
            self._task_callback,
            callback_group=self._task_cb_group
        )

        # --- Service client (sam3_node) ---
        self._get_pose_client = self.create_client(
            GetPose, 'get_pose',
            callback_group=self._client_cb_group
        )

        # --- Service client (vlm_node) ---
        self._vlm_client = self.create_client(
            VlmJudge, 'vlm_judge',
            callback_group=self._client_cb_group
        )

        # --- Action client (robot_node) ---
        self._robot_client = ActionClient(
            self, Move, 'move',
            callback_group=self._client_cb_group
        )

        # --- Wait for dependencies ---
        self.get_logger().info('Waiting for sam3_node get_pose service...')
        if not self._get_pose_client.wait_for_service(timeout_sec=120.0):
            raise RuntimeError('sam3_node get_pose service not available')

        self.get_logger().info('Waiting for vlm_node vlm_judge service...')
        if not self._vlm_client.wait_for_service(timeout_sec=120.0):
            raise RuntimeError('vlm_node vlm_judge service not available')

        self.get_logger().info('Waiting for robot move action server...')
        if not self._robot_client.wait_for_server(timeout_sec=120.0):
            raise RuntimeError('robot move action server not available')

        self.get_logger().info('orchestration_node ready. Service: pick_place_task')
        self._state = self.STATE_IDLE

    def _load_pose_param(self, name):
        """Load a 6-element pose parameter as list."""
        values = list(self.get_parameter(name).get_parameter_value().double_array_value)
        if len(values) != 6:
            raise ValueError(
                f"Parameter '{name}' must have 6 elements [x,y,z,r,p,y], got {len(values)}"
            )
        self.get_logger().info(
            f"Loaded {name}: [{values[0]:.3f}, {values[1]:.3f}, {values[2]:.3f}, "
            f"{values[3]:.2f}, {values[4]:.2f}, {values[5]:.2f}]"
        )
        return values

    # ------------------------------------------------------------------
    # Robot action helper
    # ------------------------------------------------------------------

    def _send_move(self, pose, label=''):
        """Send a Move goal to robot and block until result.

        Args:
            pose: list of 6 floats [x, y, z, roll, pitch, yaw].
            label: human-readable name for logging.

        Returns:
            bool: True if action succeeded.
        """
        self.get_logger().info(
            f'[{label}] Move goal: '
            f'x={pose[0]:.4f} y={pose[1]:.4f} z={pose[2]:.4f} '
            f'r={pose[3]:.2f} p={pose[4]:.2f} y={pose[5]:.2f}'
        )
        goal = Move.Goal()
        goal.target_pose = pose

        future = self._robot_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'[{label}] Move goal rejected')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result.success

    # ------------------------------------------------------------------
    # Perception helper
    # ------------------------------------------------------------------

    def _call_get_pose(self, object_name):
        """Call sam3_node get_pose service. Returns float64[6] or None if not detected."""
        req = GetPose.Request()
        req.method = object_name
        future = self._get_pose_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        pose = list(result.pose)
        if pose == _ZERO_POSE:
            return None
        return pose

    def _call_vlm_judge(self, image_paths, object_name, return_reason):
        """Call vlm_node vlm_judge service. Returns (decision, reason) or None on failure."""
        req = VlmJudge.Request()
        req.image_paths = image_paths
        req.object_name = object_name
        req.return_reason = return_reason
        future = self._vlm_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        if not result.success:
            self.get_logger().error(f'VLM judge failed: {result.reason}')
            return None
        self.get_logger().info(
            f'VLM result: {result.decision} '
            f'(damage={result.damage_status}, {result.inference_time:.2f}s)'
        )
        return result

    # ------------------------------------------------------------------
    # Main state machine
    # ------------------------------------------------------------------

    def _task_callback(self, request, response):
        """Execute pick-validate-place cycle.

        State machine flow:
            init -> sam3(get_pose) -> pick -> val -> sam3(validate)
            -> detected:  place -> init -> success
            -> not detected: place_return -> retry
        """
        object_name = request.payload
        self.get_logger().info(f'=== Task received: "{object_name}" ===')

        retry_count = 0

        while True:
            # 1. Move to init pose
            self._state = self.STATE_INIT_POSE
            self.get_logger().info(f'[State: INIT_POSE] (retry={retry_count})')
            if not self._send_move(self.init_pose, 'INIT_POSE'):
                response.success = False
                self._state = self.STATE_IDLE
                return response

            # 2. Get pick pose from sam3
            self._state = self.STATE_GET_PICK_POSE
            self.get_logger().info(f'[State: GET_PICK_POSE] object="{object_name}"')
            pick_pose = self._call_get_pose(object_name)
            if pick_pose is None:
                self.get_logger().error(f'sam3 failed to detect "{object_name}"')
                response.success = False
                self._state = self.STATE_IDLE
                return response

            # 3. Move to pick pose (dynamic, from sam3)
            self._state = self.STATE_PICK_POSE
            self.get_logger().info('[State: PICK_POSE]')
            if not self._send_move(pick_pose, 'PICK_POSE'):
                response.success = False
                self._state = self.STATE_IDLE
                return response

            # 4. Move to validation pose
            self._state = self.STATE_VAL_POSE
            self.get_logger().info('[State: VAL_POSE]')
            if not self._send_move(self.val_pose, 'VAL_POSE'):
                response.success = False
                self._state = self.STATE_IDLE
                return response

            # 5. Validate: call get_pose again, object detected = valid
            self._state = self.STATE_VALIDATE
            self.get_logger().info(f'[State: VALIDATE] object="{object_name}"')
            val_pose = self._call_get_pose(object_name)
            is_valid = val_pose is not None

            if is_valid:
                # 6a. SUCCESS: place object
                self._state = self.STATE_PLACE_POSE
                self.get_logger().info('[State: PLACE_POSE] Validation PASSED')
                if not self._send_move(self.place_pose, 'PLACE_POSE'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                # Return to init
                if not self._send_move(self.init_pose, 'RETURN_TO_INIT'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                response.success = True
                self.get_logger().info(
                    f'=== Task SUCCESS for "{object_name}" (retries={retry_count}) ==='
                )
                self._state = self.STATE_IDLE
                return response
            else:
                # 6b. RETRY: return defective item
                retry_count += 1
                self._state = self.STATE_PLACE_RETURN
                self.get_logger().warn(
                    f'[State: PLACE_RETURN] Validation FAILED, retry {retry_count}'
                )
                if not self._send_move(self.place_return_pose, 'PLACE_RETURN'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response


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
