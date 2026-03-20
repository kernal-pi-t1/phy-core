"""SAM3 perception node for pick-and-place orchestration.

Wraps PoseEstimator (pose_estimator.py:184) and capture_single_frame
(capture_realsense.py:5) as ROS2 service servers.

Services:
    get_pick_pose (GetPickPose.srv): Detect object and return 6DoF pick pose
    validate_object (ValidateObject.srv): Detect object presence for validation
"""

import threading

import rclpy
from rclpy.node import Node

from pick_place_interfaces.srv import GetPickPose, ValidateObject


class Sam3Node(Node):
    """ROS2 node providing SAM3-based perception services."""

    def __init__(self):
        super().__init__('sam3_node')

        # Declare parameters
        self.declare_parameter('device', 'cuda')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('fx', 0.0)
        self.declare_parameter('fy', 0.0)
        self.declare_parameter('cx', 0.0)
        self.declare_parameter('cy', 0.0)

        device = self.get_parameter('device').get_parameter_value().string_value
        confidence = self.get_parameter('confidence_threshold').get_parameter_value().double_value
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

        # Load PoseEstimator (SAM3 model loads here, ~10-30s)
        self.get_logger().info(
            f'Loading PoseEstimator (device={device}, confidence={confidence})...'
        )
        from pose_estimator import PoseEstimator
        self._estimator = PoseEstimator(
            device=device, confidence_threshold=confidence
        )
        self.get_logger().info('PoseEstimator loaded successfully.')

        # Import capture function
        from capture_realsense import capture_single_frame
        self._capture = capture_single_frame

        # Lock for thread safety (SAM3 GPU model is not thread-safe)
        self._lock = threading.Lock()

        # Service servers
        self._get_pose_srv = self.create_service(
            GetPickPose, 'get_pick_pose', self._get_pick_pose_callback
        )
        self._validate_srv = self.create_service(
            ValidateObject, 'validate_object', self._validate_object_callback
        )

        self.get_logger().info('sam3_node ready. Services: get_pick_pose, validate_object')

    def _get_pick_pose_callback(self, request, response):
        """Capture image, run SAM3 segmentation+pose, return first detected pose."""
        self.get_logger().info(f"get_pick_pose called for object: '{request.object_name}'")
        try:
            with self._lock:
                depth_mm, color_bgr = self._capture()
                intrinsics = (self.fx, self.fy, self.cx, self.cy)
                poses = self._estimator.estimate_poses(
                    color_bgr, depth_mm, intrinsics,
                    prompt=request.object_name, is_bgr=True
                )
            if poses:
                p = poses[0]  # Take first detection
                response.success = True
                response.pose.x = p.x
                response.pose.y = p.y
                response.pose.z = p.z
                response.pose.roll = p.roll
                response.pose.pitch = p.pitch
                response.pose.yaw = p.yaw
                self.get_logger().info(
                    f'Detected pose: x={p.x:.4f} y={p.y:.4f} z={p.z:.4f} '
                    f'r={p.roll:.2f} p={p.pitch:.2f} y={p.yaw:.2f}'
                )
            else:
                response.success = False
                response.error_message = f"No object '{request.object_name}' detected"
                self.get_logger().warn(response.error_message)
        except Exception as e:
            self.get_logger().error(f'get_pick_pose failed: {e}')
            response.success = False
            response.error_message = str(e)
        return response

    def _validate_object_callback(self, request, response):
        """Capture image, run SAM3 segmentation, return whether object is detected."""
        self.get_logger().info(f"validate_object called for object: '{request.object_name}'")
        try:
            with self._lock:
                depth_mm, color_bgr = self._capture()
                intrinsics = (self.fx, self.fy, self.cx, self.cy)
                poses = self._estimator.estimate_poses(
                    color_bgr, depth_mm, intrinsics,
                    prompt=request.object_name, is_bgr=True
                )
            response.is_valid = len(poses) > 0
            self.get_logger().info(
                f"Validation result for '{request.object_name}': "
                f"{'VALID' if response.is_valid else 'INVALID'} "
                f"({len(poses)} detections)"
            )
        except Exception as e:
            self.get_logger().error(f'validate_object failed: {e}')
            response.is_valid = False
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
