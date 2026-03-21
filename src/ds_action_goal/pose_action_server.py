#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from sensor_msgs.msg import JointState  # 현재 관절 상태 확인용
from std_srvs.srv import Trigger
from dsr_msgs2.srv import Ikin, MoveJoint
from phy_interface.action import Move

class PoseActionServer(Node):
    def __init__(self):
        super().__init__('pose_action_server')

        # 재진입 가능한 콜백 그룹 설정 (Deadlock 방지 핵심)
        self.callback_group = ReentrantCallbackGroup()

        # 파라미터 선언
        self.declare_parameter('namespace', 'dsr01')
        self.declare_parameter('ik_service_name', '')
        self.declare_parameter('move_service_name', '')
        self.declare_parameter('sol_space', 0)
        self.declare_parameter('ref', 0)
        self.declare_parameter('default_vel', 30.0)
        self.declare_parameter('default_acc', 30.0)

        self.namespace = self.get_parameter('namespace').value
        self.sol_space = int(self.get_parameter('sol_space').value)
        self.ref = int(self.get_parameter('ref').value)
        self.default_vel = float(self.get_parameter('default_vel').value)
        self.default_acc = float(self.get_parameter('default_acc').value)

        # 서비스 및 토픽 이름 설정
        ik_srv = self.get_parameter('ik_service_name').value
        self.ik_service_name = ik_srv if ik_srv else f'/{self.namespace}/motion/ikin'
        
        move_srv = self.get_parameter('move_service_name').value
        self.move_service_name = move_srv if move_srv else f'/{self.namespace}/motion/move_joint'

        # 1. 현재 관절 상태 구독 (필터링 로직 확장용)
        self.current_joints = [0.0] * 6
        self.joint_sub = self.create_subscription(
            JointState,
            f'/{self.namespace}/joint_states',
            self.joint_state_callback,
            10,
            callback_group=self.callback_group
        )

        # 2. 서비스 클라이언트 생성
        self.ik_client = self.create_client(Ikin, self.ik_service_name, callback_group=self.callback_group)
        self.move_client = self.create_client(MoveJoint, self.move_service_name, callback_group=self.callback_group)

        # 2.5. 그리퍼 서비스 클라이언트 생성
        self.gripper_open_client = self.create_client(
            Trigger, f'/{self.namespace}/gripper/open',
            callback_group=self.callback_group
        )
        self.gripper_close_client = self.create_client(
            Trigger, f'/{self.namespace}/gripper/close',
            callback_group=self.callback_group
        )
        self.gripper_is_open = True  # 초기 상태: open

        # 3. 액션 서버 생성
        self._action_server = ActionServer(
            self,
            Move,
            'pose_to_joint',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('========================================')
        self.get_logger().info('Pose Action Server (Safe Move) Started')
        self.get_logger().info(f'Namespace: {self.namespace}')
        self.get_logger().info('========================================')

    def joint_state_callback(self, msg):
        """현재 로봇의 관절 각도를 실시간 업데이트"""
        # 보통 msg.position은 라디안 단위입니다. 
        # 두산 서비스(degree)와 비교하려면 변환이 필요할 수 있으나, 
        # 여기서는 Ikin 결과값인 degree를 기준으로 한계 검사를 수행합니다.
        self.current_joints = list(msg.position)

    def is_joint_limit_ok(self, joints):
        """계산된 조인트가 물리적 한계 내에 있는지 검사 (Doosan E0509 기준)"""
        # 단위: 도(Degree) / 각 관절의 Max-Min 범위
        limits = [360.0, 360.0, 155.0, 360.0, 155.0, 360.0]
        
        for i, j_val in enumerate(joints):
            if abs(j_val) > limits[i]:
                self.get_logger().warn(f'⚠️ J{i+1} 한계 초과: {j_val:.2f} (Limit: {limits[i]})')
                return False
        return True

    def goal_callback(self, goal_request):
        if len(goal_request.target_pose) != 6:
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        result = Move.Result()
        feedback = Move.Feedback()

        try:
            target_pose = list(goal_handle.request.target_pose)
            
            # Step 1: IK 계산
            feedback.status = 'Step 1: Calculating IK...'
            goal_handle.publish_feedback(feedback)
            joints = await self.calculate_joints_with_ikin(target_pose)

            if joints is None:
                self.get_logger().error('IK Calculation failed (No Solution).')
                goal_handle.abort()
                result.success = False
                return result

            # [핵심] Step 2: 조인트 한계 검사 (필터링)
            joint_str = ", ".join([f"{j:.3f}" for j in joints])
            self.get_logger().info(f'★★★ 계산된 조인트 6개: [{joint_str}] ★★★')

            if not self.is_joint_limit_ok(joints):
                self.get_logger().error('IK Solution exists but violates Joint Limits!')
                goal_handle.abort()
                result.success = False
                return result

            # Step 3: 실제 로봇 이동 명령 호출
            feedback.status = 'Step 2: Moving robot...'
            goal_handle.publish_feedback(feedback)
            
            self.get_logger().info('Sending MoveJoint service request...')
            move_success = await self.call_move_joint_service(joints)

            if not move_success:
                self.get_logger().error('Movement service rejected or failed.')
                goal_handle.abort()
                result.success = False
                return result

            # Step 4: grip=True이면 그리퍼 상태 토글
            grip = goal_handle.request.grip
            if grip:
                feedback.status = 'Step 3: Toggling gripper...'
                goal_handle.publish_feedback(feedback)
                await self.toggle_gripper()

            self.get_logger().info('Action finished successfully!')
            goal_handle.succeed()
            result.success = True
            return result

        except Exception as e:
            self.get_logger().error(f'Unexpected Error: {e}')
            goal_handle.abort()
            result.success = False
            return result

    async def toggle_gripper(self):
        """그리퍼 상태 토글: open→close, close→open"""
        if self.gripper_is_open:
            client = self.gripper_close_client
            action = 'CLOSE'
        else:
            client = self.gripper_open_client
            action = 'OPEN'

        if not client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error(f'Gripper {action} service not available')
            return

        try:
            resp = await client.call_async(Trigger.Request())
            if resp.success:
                self.gripper_is_open = not self.gripper_is_open
                self.get_logger().info(f'Gripper toggled → {action}')
            else:
                self.get_logger().error(f'Gripper {action} failed: {resp.message}')
        except Exception as e:
            self.get_logger().error(f'Gripper {action} error: {e}')

    async def calculate_joints_with_ikin(self, target_pose):
        if not self.ik_client.wait_for_service(timeout_sec=2.0):
            return None

        req = Ikin.Request()
        req.pos = [float(v) for v in target_pose]
        req.sol_space = self.sol_space
        req.ref = self.ref

        try:
            resp = await self.ik_client.call_async(req)
            if hasattr(resp, 'conv_posj'):
                return list(resp.conv_posj)
            elif hasattr(resp, 'posj'):
                return list(resp.posj)
            return None
        except Exception:
            return None

    async def call_move_joint_service(self, joints):
        if not self.move_client.wait_for_service(timeout_sec=2.0):
            return False

        req = MoveJoint.Request()
        req.pos = [float(j) for j in joints]
        req.vel = self.default_vel
        req.acc = self.default_acc
        req.time = 0.0
        req.radius = 0.0
        req.mode = 0
        req.blend_type = 0
        req.sync_type = 0

        try:
            resp = await self.move_client.call_async(req)
            return resp.success
        except Exception:
            return False

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    node = PoseActionServer()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
    