#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pose Action Server - MoveLine 기반 TCP 이동 + 그리퍼 제어

액션 인터페이스: Move.action
    Goal:  float64[6] target_pose (x, y, z, roll, pitch, yaw)
           bool grip (true=닫기, false=열기)
    Result: bool success
    Feedback: string status

사용법:
    # 베이스 좌표계 (기본)
    ros2 run phy_core action_node

    # 툴 좌표계
    ros2 run phy_core action_node --ros-args -p frame:=tool

골 보내기:
    # 베이스 좌표계 절대 위치 이동 + 그리퍼 닫기
    ros2 action send_goal /pose_to_joint phy_interface/action/Move \
        "{target_pose: [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], grip: true}"

    # 툴 좌표계 상대 이동 (Z +10mm만)
    ros2 action send_goal /pose_to_joint phy_interface/action/Move \
        "{target_pose: [0.0, 0.0, 10.0, 0.0, 0.0, 0.0], grip: false}"
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from dsr_msgs2.srv import MoveLine, MoveJoint, GetCurrentPosx
from std_msgs.msg import Int32
from std_srvs.srv import Trigger
from phy_interface.action import Move

# Doosan 좌표계 상수
DR_BASE = 0
DR_TOOL = 1


class PoseActionServer(Node):
    def __init__(self):
        super().__init__('pose_action_server')

        self.callback_group = ReentrantCallbackGroup()

        # 파라미터
        self.declare_parameter('namespace', 'dsr01')
        self.declare_parameter('frame', 'base')        # base 또는 tool
        self.declare_parameter('default_vel', 100.0)    # mm/s
        self.declare_parameter('default_acc', 100.0)    # mm/s²

        self.namespace = self.get_parameter('namespace').value
        self.frame = self.get_parameter('frame').value  # 'base' or 'tool'
        self.default_vel = float(self.get_parameter('default_vel').value)
        self.default_acc = float(self.get_parameter('default_acc').value)

        # 서비스 클라이언트
        self.move_line_client = self.create_client(
            MoveLine,
            f'/{self.namespace}/motion/move_line',
            callback_group=self.callback_group)

        self.move_joint_client = self.create_client(
            MoveJoint,
            f'/{self.namespace}/motion/move_joint',
            callback_group=self.callback_group)

        self.get_posx_client = self.create_client(
            GetCurrentPosx,
            f'/{self.namespace}/aux_control/get_current_posx',
            callback_group=self.callback_group)

        self.gripper_open_client = self.create_client(
            Trigger,
            f'/{self.namespace}/gripper/open',
            callback_group=self.callback_group)

        self.gripper_close_client = self.create_client(
            Trigger,
            f'/{self.namespace}/gripper/close',
            callback_group=self.callback_group)

        # 그리퍼 토크 구독
        self.declare_parameter('torque_threshold', 30)
        self.torque_threshold = self.get_parameter('torque_threshold').value
        self._last_torque = -1
        self.torque_sub = self.create_subscription(
            Int32,
            f'/{self.namespace}/gripper/torque',
            self._torque_callback,
            10,
            callback_group=self.callback_group)

        # 액션 서버
        self._action_server = ActionServer(
            self,
            Move,
            'pose_to_joint',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        frame_kr = '베이스' if self.frame == 'base' else '툴'
        self.get_logger().info(f'  토크 임계값: {self.torque_threshold}')
        self.get_logger().info('========================================')
        self.get_logger().info('Pose Action Server (MoveLine) Started')
        self.get_logger().info(f'  Namespace: {self.namespace}')
        self.get_logger().info(f'  좌표계: {frame_kr} ({self.frame})')
        self.get_logger().info(f'  속도: {self.default_vel} mm/s')
        self.get_logger().info('========================================')

    def goal_callback(self, goal_request):
        if len(goal_request.target_pose) != 6:
            self.get_logger().warn('target_pose 길이가 6이 아님 → 거부')
            return GoalResponse.REJECT
        if goal_request.method not in ('fk', 'ik', ''):
            self.get_logger().warn(f'잘못된 method: "{goal_request.method}" → 거부')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('이동 취소 요청')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        result = Move.Result()
        feedback = Move.Feedback()

        try:
            target_pose = list(goal_handle.request.target_pose)
            grip = goal_handle.request.grip
            method = goal_handle.request.method or 'ik'

            # Step 1: 현재 좌표 확인
            feedback.status = '현재 좌표 조회 중...'
            goal_handle.publish_feedback(feedback)

            current = await self.get_current_pose()
            if current is not None:
                self.get_logger().info(
                    f'현재 좌표: [{", ".join(f"{v:.1f}" for v in current)}]')

            # Step 2: 이동
            if method == 'fk':
                # FK: MoveJoint으로 조인트 각도 직접 전달
                feedback.status = f'FK 이동 (MoveJoint): [{", ".join(f"{v:.1f}" for v in target_pose)}]'
                goal_handle.publish_feedback(feedback)
                move_ok = await self.call_move_joint(target_pose)
            elif self.frame == 'tool':
                # IK 툴 좌표계: target_pose를 상대값으로 사용
                feedback.status = f'툴 좌표계 상대이동: [{", ".join(f"{v:.1f}" for v in target_pose)}]'
                goal_handle.publish_feedback(feedback)
                move_ok = await self.call_move_line(
                    target_pose, ref=DR_TOOL, mode=1)  # mode=1: 상대이동
            else:
                # IK 베이스 좌표계: target_pose를 절대좌표로 사용
                feedback.status = f'베이스 좌표계 이동: [{", ".join(f"{v:.1f}" for v in target_pose)}]'
                goal_handle.publish_feedback(feedback)
                move_ok = await self.call_move_line(
                    target_pose, ref=DR_BASE, mode=0)  # mode=0: 절대이동

            if not move_ok:
                self.get_logger().error('MoveLine 실패')
                goal_handle.abort()
                result.success = False
                return result

            self.get_logger().info('이동 완료!')

            # Step 3: 그리퍼 제어
            feedback.status = f'그리퍼 {"닫기" if grip else "열기"}...'
            goal_handle.publish_feedback(feedback)

            grip_ok = await self.control_gripper(grip)
            if not grip_ok:
                self.get_logger().warn('그리퍼 제어 실패 (이동은 성공)')

            # Step 4: 최종 좌표 확인
            final = await self.get_current_pose()
            if final is not None:
                self.get_logger().info(
                    f'최종 좌표: [{", ".join(f"{v:.1f}" for v in final)}]')

            goal_handle.succeed()
            result.success = True
            return result

        except Exception as e:
            self.get_logger().error(f'에러: {e}')
            goal_handle.abort()
            result.success = False
            return result

    async def get_current_pose(self):
        """현재 TCP 좌표 조회"""
        if not self.get_posx_client.wait_for_service(timeout_sec=3.0):
            return None

        req = GetCurrentPosx.Request()
        req.ref = DR_BASE

        try:
            resp = await self.get_posx_client.call_async(req)
            if resp.success and len(resp.task_pos_info) > 0:
                return list(resp.task_pos_info[0].data)[:6]
        except Exception:
            pass
        return None

    async def call_move_line(self, pose, ref=DR_BASE, mode=0):
        """MoveLine 서비스 호출"""
        if not self.move_line_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().error('move_line 서비스 연결 실패')
            return False

        req = MoveLine.Request()
        req.pos = [float(v) for v in pose]
        req.vel = [self.default_vel, 30.0]   # [mm/s, deg/s]
        req.acc = [self.default_acc, 30.0]   # [mm/s², deg/s²]
        req.time = 0.0
        req.radius = 0.0
        req.ref = ref
        req.mode = mode
        req.blend_type = 0
        req.sync_type = 0   # SYNC

        try:
            resp = await self.move_line_client.call_async(req)
            return resp.success
        except Exception as e:
            self.get_logger().error(f'MoveLine 호출 에러: {e}')
            return False

    async def call_move_joint(self, joints, mode=0):
        """MoveJoint 서비스 호출 (FK)"""
        if not self.move_joint_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().error('move_joint 서비스 연결 실패')
            return False

        req = MoveJoint.Request()
        req.pos = [float(v) for v in joints]
        req.vel = 60.0    # deg/s
        req.acc = 60.0    # deg/s²
        req.time = 0.0
        req.radius = 0.0
        req.mode = mode
        req.blend_type = 0
        req.sync_type = 0   # SYNC

        try:
            resp = await self.move_joint_client.call_async(req)
            return resp.success
        except Exception as e:
            self.get_logger().error(f'MoveJoint 호출 에러: {e}')
            return False

    def _torque_callback(self, msg):
        self._last_torque = msg.data

    async def control_gripper(self, grip):
        """그리퍼 제어 (grip=True→닫기, False→열기). 닫기 시 토크로 파지 판단."""
        client = self.gripper_close_client if grip else self.gripper_open_client
        action_name = '닫기' if grip else '열기'

        if not client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn(f'gripper/{action_name} 서비스 없음 (스킵)')
            return False

        try:
            self._last_torque = -1
            resp = await client.call_async(Trigger.Request())
            if resp.success:
                self.get_logger().info(f'그리퍼 {action_name} 완료: {resp.message}')
            else:
                self.get_logger().warn(f'그리퍼 {action_name} 실패: {resp.message}')
                return False

            # 닫기 시 토크 기반 파지 판단
            if grip:
                torque = self._last_torque
                if torque != -1 and torque < self.torque_threshold:
                    self.get_logger().warn(
                        f'파지 실패 (torque={torque} < {self.torque_threshold})')
                    return False
                self.get_logger().info(f'파지 확인 (torque={torque})')

            return True
        except Exception as e:
            self.get_logger().error(f'그리퍼 에러: {e}')
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
