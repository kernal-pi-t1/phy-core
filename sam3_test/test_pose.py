"""SAM3 + Pose estimation test — detect objects and estimate 6DoF poses."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sam3"))

import numpy as np
import cv2


def main():
    from capture_realsense import capture_single_frame
    from pose_estimator import PoseEstimator
    import pyrealsense2 as rs

    print("=== SAM3 + Pose Estimation Test ===")

    # 1. Get intrinsics
    print("\n[1/3] Getting camera intrinsics...")
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)
    print(f"  fx={intr.fx:.1f} fy={intr.fy:.1f} cx={intr.ppx:.1f} cy={intr.ppy:.1f}")

    # 2. Capture
    print("\n[2/3] Capturing...")
    depth_mm, color_bgr = capture_single_frame()
    print(f"  Color: {color_bgr.shape}, Depth: {depth_mm.shape}")

    # 3. Estimate poses
    print("\n[3/3] Running pose estimation...")
    estimator = PoseEstimator(device="cuda", confidence_threshold=0.5)

    t0 = time.perf_counter()
    poses = estimator.estimate_poses(
        color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True
    )
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"\n  Inference: {elapsed:.1f}ms")
    print(f"  Objects detected: {len(poses)}")

    for i, p in enumerate(poses):
        print(f"  [Object {i}] x={p.x:.4f}m y={p.y:.4f}m z={p.z:.4f}m "
              f"roll={p.roll:.1f}° pitch={p.pitch:.1f}° yaw={p.yaw:.1f}°")

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(os.path.join(out_dir, "pose_input.png"), color_bgr)
    print(f"\n  Saved: {out_dir}/pose_input.png")
    print(f"\n=== RESULT: {len(poses)} poses, {elapsed:.1f}ms ===")


if __name__ == "__main__":
    main()
