"""Pick-and-place orchestration node.

State machine that coordinates robot_node (Move action) and sam3_node
(GetPose service) for pick-validate-place cycles.

Receives prompts via Json service, orchestrates the full cycle:
init_pose -> get_pose -> Camera→Base Transform -> [Pre-Grasp -> Descend -> Close Gripper -> Lift]
-> val_pose -> VLM validate -> place/retry

Threading model:
    - MultiThreadedExecutor with dual callback groups
    - MutuallyExclusiveCallbackGroup for service server
    - ReentrantCallbackGroup for outbound clients
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient

from std_msgs.msg import Int32
from std_srvs.srv import Trigger
try:
    from dsr_msgs2.srv import FlangeSerialOpen, FlangeSerialClose, FlangeSerialWrite, FlangeSerialRead
    FLANGE_SERIAL_DEPS = True
except ImportError:
    FLANGE_SERIAL_DEPS = False
from phy_interface.srv import Json, GetPose, CountObjects, VlmJudge
from phy_interface.action import Move
from phy_core.transform import CameraToBaseTransform

_ZERO_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

class OrchestrationNode(Node):
    """State machine orchestrating pick-validate-place cycles."""

    STATE_IDLE = 'IDLE'
    STATE_INIT_POSE = 'INIT_POSE'
    STATE_GET_PICK_POSE = 'GET_PICK_POSE'
    STATE_PICK_EXECUTE = 'PICK_EXECUTE'
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

        self.init_pose = self._load_pose_param('init_pose')
        self.val_pose = self._load_pose_param('val_pose')
        self.place_pose = self._load_pose_param('place_pose')
        self.place_return_pose = self._load_pose_param('place_return_pose')

        # --- Camera extrinsics (fixed camera → base frame) ---
        self.declare_parameter('camera_offset', [0.80, 0.0, 0.66])
        self.declare_parameter('camera_rpy', [0.0, 0.0, 0.0])
        self.camera_offset = list(
            self.get_parameter('camera_offset').get_parameter_value().double_array_value
        )
        camera_rpy_deg = list(
            self.get_parameter('camera_rpy').get_parameter_value().double_array_value
        )
        self._cam_to_base = CameraToBaseTransform(self.camera_offset, camera_rpy_deg)
        self.get_logger().info(f'Camera offset: {self.camera_offset}, rpy(deg): {camera_rpy_deg}')

        # --- Service server (entry point) ---
        self._task_service = self.create_service(
            Json, 'pick_place_task',
            self._task_callback,
            callback_group=self._task_cb_group
        )

        # --- Service clients (sam3_node) ---
        self._get_pose_client = self.create_client(
            GetPose, 'get_pose',
            callback_group=self._client_cb_group
        )
        self._count_objects_client = self.create_client(
            CountObjects, 'count_objects',
            callback_group=self._client_cb_group
        )

        # --- Service client (vlm_node) ---
        self._vlm_client = self.create_client(
            VlmJudge, 'vlm_judge',
            callback_group=self._client_cb_group
        )

        # --- Action client (robot motion) ---
        self._robot_client = ActionClient(
            self, Move, 'pose_to_joint',
            callback_group=self._client_cb_group
        )

        # --- Gripper Clients ---
        self.gripper_open_client = self.create_client(
            Trigger, '/dsr01/gripper/open',
            callback_group=self._client_cb_group
        )
        self.gripper_close_client = self.create_client(
            Trigger, '/dsr01/gripper/close',
            callback_group=self._client_cb_group
        )
        self.gripper_pos_pub = self.create_publisher(
            Int32, '/dsr01/gripper/position_cmd', 10
        )

        # --- Flange Serial Clients for Modbus Polling ---
        if FLANGE_SERIAL_DEPS:
            self.flange_open_cli = self.create_client(
                FlangeSerialOpen, '/dsr01/gripper/flange_serial_open',
                callback_group=self._client_cb_group
            )
            self.flange_write_cli = self.create_client(
                FlangeSerialWrite, '/dsr01/gripper/flange_serial_write',
                callback_group=self._client_cb_group
            )
            self.flange_read_cli = self.create_client(
                FlangeSerialRead, '/dsr01/gripper/flange_serial_read',
                callback_group=self._client_cb_group
            )
            self.flange_close_cli = self.create_client(
                FlangeSerialClose, '/dsr01/gripper/flange_serial_close',
                callback_group=self._client_cb_group
            )
        else:
            self.get_logger().warn('FlangeSerial services not available. Torque reading disabled.')
            self.flange_open_cli = None
            self.flange_write_cli = None
            self.flange_read_cli = None
            self.flange_close_cli = None

        # --- Wait for dependencies ---
        self.get_logger().info('Waiting for sam3_node get_pose service...')
        if not self._get_pose_client.wait_for_service(timeout_sec=120.0):
            raise RuntimeError('sam3_node get_pose service not available')

        self.get_logger().info('Waiting for sam3_node count_objects service...')
        if not self._count_objects_client.wait_for_service(timeout_sec=120.0):
            raise RuntimeError('sam3_node count_objects service not available')

        self.get_logger().info('Waiting for vlm_node vlm_judge service...')
        if not self._vlm_client.wait_for_service(timeout_sec=120.0):
            raise RuntimeError('vlm_node vlm_judge service not available')

        self.get_logger().info('Waiting for robot Move action server (/pose_to_joint)...')
        if not self._robot_client.wait_for_server(timeout_sec=120.0):
            raise RuntimeError('robot Move action server not available')

        self.get_logger().info('orchestration_node ready. Service: pick_place_task')
        self._state = self.STATE_IDLE

    def _load_pose_param(self, name):
        values = list(self.get_parameter(name).get_parameter_value().double_array_value)
        if len(values) != 6:
            raise ValueError(f"Parameter '{name}' must have 6 elements, got {len(values)}")
        self.get_logger().info(f"Loaded {name}: {values}")
        return values

    # ------------------------------------------------------------------
    # Coordinate Transform Helper (Fixed Camera → Base Frame)
    # ------------------------------------------------------------------
    def _transform_pose(self, camera_pose_arr):
        """Transform float64[6] pose from camera optical frame to base frame."""
        transformed = self._cam_to_base.transform_pose(camera_pose_arr)
        self.get_logger().info(
            f'[Transform] cam={camera_pose_arr[:3]} → base={transformed[:3]}'
        )
        return transformed

    # ------------------------------------------------------------------
    # Robot Action & Gripper Helper
    # ------------------------------------------------------------------
    def _send_move(self, pose, label='', grip=False, method='ik'):
        self.get_logger().info(
            f'[{label}] Move goal ({method}): '
            f'x={pose[0]:.4f} y={pose[1]:.4f} z={pose[2]:.4f} '
            f'r={pose[3]:.2f} p={pose[4]:.2f} y={pose[5]:.2f}'
            f'{" (grip=TOGGLE)" if grip else ""}'
        )
        goal = Move.Goal()
        goal.target_pose = pose
        goal.grip = grip
        goal.method = method

        try:
            future = self._robot_client.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, future)
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().error(f'[{label}] Move goal rejected')
                return False

            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)
            return result_future.result().result.success
        except Exception as e:
            self.get_logger().error(f'[{label}] Move action failed: {e}')
            return False

    def _open_gripper(self):
        self.get_logger().info('[GRIPPER] OPEN')
        try:
            if self.gripper_open_client.service_is_ready():
                req = Trigger.Request()
                future = self.gripper_open_client.call_async(req)
                rclpy.spin_until_future_complete(self, future)
        except Exception as e:
            self.get_logger().error(f'[GRIPPER] Trigger OPEN failed: {e}')

        msg = Int32()
        msg.data = 0
        self.gripper_pos_pub.publish(msg)
        time.sleep(1.0)

    def _close_gripper(self):
        self.get_logger().info('[GRIPPER] CLOSE')
        try:
            if self.gripper_close_client.service_is_ready():
                req = Trigger.Request()
                future = self.gripper_close_client.call_async(req)
                rclpy.spin_until_future_complete(self, future)
        except Exception as e:
            self.get_logger().error(f'[GRIPPER] Trigger CLOSE failed: {e}')

        msg = Int32()
        msg.data = 700
        self.gripper_pos_pub.publish(msg)
        time.sleep(1.0)

    def _read_gripper_torque(self):
        """플랜지 시리얼을 점유하여 Modbus FC03으로 그리퍼 전류(Torque)를 측정하고 포트를 닫습니다."""
        if self.flange_open_cli is None:
            self.get_logger().warn('[GRIPPER] FlangeSerial not available. Skipping torque read.')
            return -1
        self.get_logger().info('[GRIPPER] 시리얼 통신 개방 및 토크(전류) 센서 폴링 시작...')
        
        # 1. Serial Open
        req_open = FlangeSerialOpen.Request()
        req_open.port = 1
        req_open.baudrate = 57600
        req_open.bytesize = 8
        req_open.parity = 0
        req_open.stopbits = 1
        
        open_fut = self.flange_open_cli.call_async(req_open)
        rclpy.spin_until_future_complete(self, open_fut)
        if not open_fut.result() or not open_fut.result().success:
            self.get_logger().error('[GRIPPER] Flange Serial 포트 열기 실패')
            return -1

        torque = -1
        try:
            # 2. Write FC03 frame
            # FC03 주소 274 (0x0112), 길이 1개 레지스터
            data = [1, 0x03, 0x01, 0x12, 0x00, 0x01]
            crc = 0xFFFF
            for b in data:
                crc ^= b
                for _ in range(8):
                    crc = (crc >> 1) ^ 0xA001 if (crc & 0x0001) else (crc >> 1)
            tx_data = data + [crc & 0xFF, (crc >> 8) & 0xFF]

            req_write = FlangeSerialWrite.Request()
            req_write.port = 1
            req_write.data = tx_data
            
            write_fut = self.flange_write_cli.call_async(req_write)
            rclpy.spin_until_future_complete(self, write_fut)
            
            if write_fut.result() and write_fut.result().success:
                time.sleep(0.5) # 그리퍼가 충분히 응답할 시간 대기
                # 3. Read FC03 Response
                req_read = FlangeSerialRead.Request()
                req_read.port = 1
                req_read.timeout = 1.0
                read_fut = self.flange_read_cli.call_async(req_read)
                rclpy.spin_until_future_complete(self, read_fut)
                
                res_read = read_fut.result()
                if res_read and res_read.success and len(res_read.data) >= 7:
                    resp = res_read.data
                    if resp[1] == 0x03:
                        torque = (resp[3] << 8) | resp[4]
                        # Signed 16-bit
                        if torque > 32767:
                            torque -= 65536
                        self.get_logger().info(f'[GRIPPER] 물리적 측정 토크(Current): {torque}')
                else:
                    self.get_logger().warn('[GRIPPER] 응답 패킷 읽기 실패 (또는 타임아웃)')
            else:
                self.get_logger().error('[GRIPPER] Modbus FC03 Write 실패')
        finally:
            # 4. Serial Close (항상 수행하여 통신 소유권 반환)
            req_close = FlangeSerialClose.Request()
            req_close.port = 1
            close_fut = self.flange_close_cli.call_async(req_close)
            rclpy.spin_until_future_complete(self, close_fut)
            
        return torque

    # ------------------------------------------------------------------
    # Perception helper
    # ------------------------------------------------------------------
    def _call_get_pose(self, object_name):
        """Call SAM3 get_pose service. Returns (pose, detected_count) or (None, 0)."""
        req = GetPose.Request()
        req.method = object_name
        try:
            future = self._get_pose_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            result = future.result()
            pose = list(result.pose)
            count = result.detected_count
            if pose == _ZERO_POSE:
                return None, count
            return pose, count
        except Exception as e:
            self.get_logger().error(f'get_pose service call failed: {e}')
            return None, 0

    def _call_count_objects(self, object_name):
        """Call SAM3 count_objects service. Returns detected count."""
        req = CountObjects.Request()
        req.method = object_name
        try:
            future = self._count_objects_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            return future.result().detected_count
        except Exception as e:
            self.get_logger().error(f'count_objects service call failed: {e}')
            return 0

    def _call_vlm_judge(self, image_paths, object_name, return_reason):
        req = VlmJudge.Request()
        req.image_paths = image_paths
        req.object_name = object_name
        req.return_reason = return_reason
        try:
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
        except Exception as e:
            self.get_logger().error(f'vlm_judge service call failed: {e}')
            return None

    # ------------------------------------------------------------------
    # Main state machine
    # ------------------------------------------------------------------
    def _task_callback(self, request, response):
        object_name = request.payload
        self.get_logger().info(f'=== Task received: "{object_name}" ===')

        retry_count = 0

        try:
            while True:
                # 1. State: Init Pose
                self._state = self.STATE_INIT_POSE
                self.get_logger().info(f'[State: INIT_POSE] (retry={retry_count})')
                if not self._send_move(self.init_pose, 'INIT_POSE', method='fk'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response
                self._open_gripper()

                # 2. State: Get Pick Pose (Vision - SAM3)
                self._state = self.STATE_GET_PICK_POSE
                self.get_logger().info(f'[State: GET_PICK_POSE] Vision for "{object_name}"')
                cam_pick_pose, _ = self._call_get_pose(object_name)
                if cam_pick_pose is None:
                    self.get_logger().error(f'Vision failed to detect "{object_name}"')
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                # 3. Coordinate Transform (TF)
                pick_pose = self._transform_pose(cam_pick_pose)

                # 4. State: Pick Execution (Pre-grasp -> Descend -> Close -> Lift)
                self._state = self.STATE_PICK_EXECUTE
                self.get_logger().info('[State: PICK_EXECUTE] Starting Gripper Sequence')
                
                # (1) Pre-Grasp (Z + 10cm)
                pre_grasp_pose = list(pick_pose)
                pre_grasp_pose[2] += 0.10
                if not self._send_move(pre_grasp_pose, 'PRE_GRASP'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                # (2) Descend + Gripper Close (grip=True: open→close)
                if not self._send_move(pick_pose, 'DESCEND', grip=True):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                # -------------------------------
                # 4.5. 1차 검수: 물리 토크(Current) 측정
                # -------------------------------
                self.get_logger().info('[State: PICK_EXECUTE] 1차 물리 검증 중...')
                time.sleep(1.0) # 꽉 쥘때까지 약간 대기
                measured_torque = self._read_gripper_torque()
                
                # 전류 수치가 30 이하면 빈 허공을 잡은 것으로 간주 (튜닝 가능)
                if measured_torque != -1 and measured_torque < 30:
                    self.get_logger().warn(f'물리적 파지 실패 (Torque={measured_torque} < 30). 물체가 없거나 떨어졌습니다.')
                    response.success = False
                    self._state = self.STATE_IDLE
                    self._open_gripper()
                    return response
                
                self.get_logger().info(f'--- 1차 물리 검증 PASSED: (Torque={measured_torque}) ---')

                # (4) Lift
                if not self._send_move(pre_grasp_pose, 'LIFT'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                # 5. State: SAM3 Recheck (파지 검증 - 잔여 객체 수 확인)
                self._state = self.STATE_VAL_POSE
                self.get_logger().info('[State: VAL_POSE] SAM3 recheck - 잔여 객체 수 확인')

                # init_pose로 이동하여 카메라 시야 확보
                if not self._send_move(self.init_pose, 'RECHECK_INIT', method='fk'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                recheck_count = self._call_count_objects(object_name)
                self.get_logger().info(f'[SAM3 Recheck] detected_count={recheck_count}')

                if recheck_count >= 3:
                    # 파지 실패: 객체가 줄지 않음 → 이전 pick point에 놓고 재시도
                    self.get_logger().warn(
                        f'[SAM3 Recheck] 잔여 객체 {recheck_count}개 (>=3) → 파지 실패, 재시도'
                    )
                    # 이전 picking point로 돌아가서 놓기
                    if not self._send_move(pick_pose, 'RETRY_RELEASE', grip=True):
                        response.success = False
                        self._state = self.STATE_IDLE
                        return response
                    retry_count += 1
                    continue  # while 루프 처음으로 → INIT_POSE부터 재시도

                # 6. State: Validate (VLM)
                self.get_logger().info(f'[SAM3 Recheck] 잔여 객체 {recheck_count}개 (<3) → 파지 성공, VLM 검증 진행')

                if not self._send_move(self.val_pose, 'VAL_POSE', method='fk'):
                    response.success = False
                    self._state = self.STATE_IDLE
                    return response

                self._state = self.STATE_VALIDATE
                self.get_logger().info(f'[State: VALIDATE] VLM Verification for "{object_name}"')

                # TODO: VLM 판단을 위해 실제 카메라 모듈의 사진 캡처 로직을 연동하세요!
                dummy_image = ['/tmp/vlm_validation_1.jpg']
                vlm_result = self._call_vlm_judge(dummy_image, object_name, "상태 검수 및 파지 여부 확인")

                is_valid = False
                if vlm_result is not None and vlm_result.decision == 'RETURN_APPROVED':
                    is_valid = True

                # 7. Classification and placement (Place & Return)
                if is_valid:
                    self._state = self.STATE_PLACE_POSE
                    self.get_logger().info('[State: PLACE_POSE] Validation PASSED')
                    # Place + Gripper Open (grip=True: close→open)
                    if not self._send_move(self.place_pose, 'PLACE_POSE', grip=True, method='fk'):
                        response.success = False
                        self._state = self.STATE_IDLE
                        return response

                    # Return to init
                    if not self._send_move(self.init_pose, 'RETURN_TO_INIT', method='fk'):
                        response.success = False
                        self._state = self.STATE_IDLE
                        return response

                    response.success = True
                    self.get_logger().info(f'=== Task SUCCESS for "{object_name}" (retries={retry_count}) ===')
                    self._state = self.STATE_IDLE
                    return response
                else:
                    retry_count += 1
                    self._state = self.STATE_PLACE_RETURN
                    self.get_logger().warn(f'[State: PLACE_RETURN] Validation FAILED (Retry {retry_count})')
                    # Place Return + Gripper Open (grip=True: close→open)
                    if not self._send_move(self.place_return_pose, 'PLACE_RETURN', grip=True, method='fk'):
                        response.success = False
                        self._state = self.STATE_IDLE
                        return response

        except Exception as e:
            self.get_logger().error(f'[FATAL Error in State Machine] {e}')
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
