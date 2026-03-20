"""SAM3 ROS2 service call test — requires sam3_node running."""

import sys
import rclpy
from rclpy.node import Node
from phy_interface.srv import GetPose


class TestClient(Node):
    def __init__(self):
        super().__init__('sam3_test_client')
        self.client = self.create_client(GetPose, 'get_pose')
        print("Waiting for /get_pose service...")
        if not self.client.wait_for_service(timeout_sec=10.0):
            print("ERROR: /get_pose service not available. Is sam3_node running?")
            sys.exit(1)
        print("Service connected.")

    def call(self, prompt):
        req = GetPose.Request()
        req.method = prompt
        future = self.client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main():
    rclpy.init()
    client = TestClient()

    prompts = sys.argv[1:] if len(sys.argv) > 1 else ["object"]

    print(f"\n=== SAM3 Service Call Test ===")
    for prompt in prompts:
        print(f"\n--- Prompt: '{prompt}' ---")
        result = client.call(prompt)
        pose = result.pose
        if all(v == 0.0 for v in pose):
            print(f"  Result: No object detected")
        else:
            print(f"  Result: x={pose[0]:.4f}m y={pose[1]:.4f}m z={pose[2]:.4f}m "
                  f"roll={pose[3]:.1f}° pitch={pose[4]:.1f}° yaw={pose[5]:.1f}°")

    client.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
