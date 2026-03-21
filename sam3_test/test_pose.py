"""SAM3 + Pose estimation test — uses PoseEstimator (same as sam3_node).

Applies crop_config.yaml if present (same as PoseEstimator).
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "phy_core"))

import numpy as np
import cv2
import yaml


CROP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_config.yaml")


def load_crop_config():
    if not os.path.exists(CROP_CONFIG_PATH):
        return None
    with open(CROP_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def main():
    from phy_core.sam3 import PoseEstimator, capture_single_frame
    import pyrealsense2 as rs
    import torch

    print("=== SAM3 + Pose Estimation Test (PoseEstimator) ===")

    # 1. Get intrinsics
    print("\n[1/4] Getting camera intrinsics...")
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)
    print(f"  fx={intr.fx:.1f} fy={intr.fy:.1f} cx={intr.ppx:.1f} cy={intr.ppy:.1f}")

    # 2. Capture
    print("\n[2/4] Capturing from RealSense...")
    depth_mm, color_bgr = capture_single_frame()
    print(f"  Color: {color_bgr.shape}, Depth: {depth_mm.shape}")

    # 3. Load crop config (for visualization)
    crop = load_crop_config()
    if crop:
        x1, y1, x2, y2 = crop
        print(f"  Crop config: ({x1},{y1})-({x2},{y2}) [{x2-x1}x{y2-y1}]")
    else:
        print("  No crop_config.yaml — using full frame")

    # 4. Estimate poses via PoseEstimator
    print("\n[3/4] Running pose estimation...")
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.008
    print(f"  confidence_threshold={threshold}")
    estimator = PoseEstimator(device="cuda", confidence_threshold=threshold)

    # Warmup
    torch.cuda.synchronize()
    _ = estimator.estimate_poses(
        color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True
    )
    torch.cuda.synchronize()

    # Timed run
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    poses = estimator.estimate_poses(
        color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True
    )
    torch.cuda.synchronize()
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"  Inference: {elapsed:.1f}ms")
    print(f"  Objects detected: {len(poses)}")

    for i, p in enumerate(poses):
        print(f"  [Object {i}] x={p.x:.4f}m y={p.y:.4f}m z={p.z:.4f}m "
              f"roll={p.roll:.1f} pitch={p.pitch:.1f} yaw={p.yaw:.1f}")

    # 5. Visualize
    print("\n[4/4] Saving visualization...")
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    cv2.imwrite(os.path.join(out_dir, "pose_input.png"), color_bgr)

    if crop:
        x1, y1, x2, y2 = crop
        color_cropped = color_bgr[y1:y2, x1:x2].copy()
    else:
        color_cropped = color_bgr

    # Draw pose info on cropped image
    overlay_crop = color_cropped.copy()
    for i, p in enumerate(poses):
        text = f"[{i}] ({p.x:.3f}, {p.y:.3f}, {p.z:.3f})m"
        cv2.putText(overlay_crop, text, (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Full frame with crop region + overlay embedded
    overlay_full = color_bgr.copy()
    if crop:
        x1, y1, x2, y2 = crop
        overlay_full[y1:y2, x1:x2] = overlay_crop
        cv2.rectangle(overlay_full, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(overlay_full, f"crop ({x1},{y1})-({x2},{y2})",
                    (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        overlay_full = overlay_crop

    cv2.imwrite(os.path.join(out_dir, "pose_overlay_crop.png"), overlay_crop)
    cv2.imwrite(os.path.join(out_dir, "pose_overlay_full.png"), overlay_full)
    print(f"  Saved: {out_dir}/pose_input.png, pose_overlay_crop.png, pose_overlay_full.png")

    # Show result on screen
    show_path = os.path.join(out_dir, "pose_overlay_full.png")
    if os.path.exists(show_path):
        import subprocess
        print(f"\nOpening: {show_path}")
        subprocess.Popen(["eog", show_path], env={**os.environ, "DISPLAY": ":0"})

    print(f"\n=== RESULT: {len(poses)} poses, {elapsed:.1f}ms ===")


if __name__ == "__main__":
    main()
