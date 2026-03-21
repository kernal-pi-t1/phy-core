"""SAM3 perception node with optimized inference.

Wraps Sam3FastProcessor + PoseEstimator as a ROS2 GetPose service.
Applies autocode-validated optimizations:
- autocast fp16 + cudnn.benchmark + torch.compile
- Cached text features
- Frame reuse (backbone skip)

Services:
    get_pose (GetPose.srv): Detect object and return 6DoF pose.
        method = object name/prompt
        pose = [x, y, z, roll, pitch, yaw] or all zeros if not detected.
"""

import threading

import rclpy
from rclpy.node import Node

from phy_interface.srv import GetPose, CountObjects


class Sam3Node(Node):
    """ROS2 node providing optimized SAM3-based perception via GetPose service."""

    def __init__(self):
        super().__init__('sam3_node')

        # Declare parameters
        self.declare_parameter('device', 'cuda')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('frame_skip', 1)
        self.declare_parameter('fx', 0.0)
        self.declare_parameter('fy', 0.0)
        self.declare_parameter('cx', 0.0)
        self.declare_parameter('cy', 0.0)

        device = self.get_parameter('device').get_parameter_value().string_value
        confidence = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        frame_skip = self.get_parameter('frame_skip').get_parameter_value().integer_value
        self.fx = self.get_parameter('fx').get_parameter_value().double_value
        self.fy = self.get_parameter('fy').get_parameter_value().double_value
        self.cx = self.get_parameter('cx').get_parameter_value().double_value
        self.cy = self.get_parameter('cy').get_parameter_value().double_value

        # Validate intrinsics
        if self.fx <= 0.0 or self.fy <= 0.0:
            self.get_logger().error(
                'Camera intrinsics fx/fy must be positive. '
                'Set fx, fy, cx, cy parameters in waypoints.yaml.'
            )
            raise RuntimeError('Invalid camera intrinsics: fx and fy must be > 0')

        # Load optimized PoseEstimator
        self.get_logger().info(
            f'Loading PoseEstimator (device={device}, confidence={confidence}, '
            f'frame_skip={frame_skip})...'
        )
        from phy_core.sam3 import PoseEstimator, capture_single_frame, camera_to_base
        self._estimator = PoseEstimator(
            device=device,
            confidence_threshold=confidence,
            frame_skip=frame_skip,
        )
        self._capture = capture_single_frame
        self._camera_to_base = camera_to_base
        self.get_logger().info('PoseEstimator loaded successfully.')

        # Lock for thread safety (SAM3 GPU model is not thread-safe)
        self._lock = threading.Lock()

        # Service servers
        self._get_pose_srv = self.create_service(
            GetPose, 'get_pose', self._get_pose_callback
        )
        self._count_objects_srv = self.create_service(
            CountObjects, 'count_objects', self._count_objects_callback
        )

        self.get_logger().info('sam3_node ready. Services: get_pose, count_objects')

    def _get_pose_callback(self, request, response):
        """Capture image, run SAM3, return first detected pose or all zeros."""
        object_name = request.method
        self.get_logger().info(f"get_pose called for: '{object_name}'")
        try:
            with self._lock:
                depth_mm, color_bgr = self._capture()
                intrinsics = (self.fx, self.fy, self.cx, self.cy)
                poses = self._estimator.estimate_poses(
                    color_bgr, depth_mm, intrinsics,
                    prompt=object_name, is_bgr=True
                )
            response.detected_count = len(poses)
            if poses:
                p = poses[0]
                bx, by, bz = self._camera_to_base(p.x, p.y, p.z)
                response.pose = [bx, by, bz, p.roll, p.pitch, p.yaw]
                self.get_logger().info(
                    f'Detected {len(poses)} object(s) (base): x={bx:.4f} y={by:.4f} z={bz:.4f} '
                    f'r={p.roll:.2f} p={p.pitch:.2f} y={p.yaw:.2f}'
                )
            else:
                response.pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                self.get_logger().warn(f"No object '{object_name}' detected")
        except Exception as e:
            self.get_logger().error(f'get_pose failed: {e}')
            response.pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        return response

    def _count_objects_callback(self, request, response):
        """Capture image, run SAM3, return detected object count."""
        object_name = request.method
        self.get_logger().info(f"count_objects called for: '{object_name}'")
        try:
            with self._lock:
                depth_mm, color_bgr = self._capture()
                intrinsics = (self.fx, self.fy, self.cx, self.cy)
                poses = self._estimator.estimate_poses(
                    color_bgr, depth_mm, intrinsics,
                    prompt=object_name, is_bgr=True
                )
            response.detected_count = len(poses)
            self.get_logger().info(f"count_objects: detected {len(poses)} object(s)")
        except Exception as e:
            self.get_logger().error(f'count_objects failed: {e}')
            response.detected_count = 0
        return response


def main(args=None):
    rclpy.init(args=args)
    node = Sam3Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
