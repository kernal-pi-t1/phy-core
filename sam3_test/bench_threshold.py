"""Benchmark script for autocode: measure detection rate and position consistency.

Outputs a single score: detection_rate * 100 + position_consistency_bonus
- detection_rate: fraction of trials detecting exactly 3 objects (0.0-1.0)
- position_consistency_bonus: if all detected, add bonus for low std (max +10)

Higher score = better. Perfect = 110.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "phy_core"))

import numpy as np
import yaml

CROP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_config.yaml")
NUM_TRIALS = 10
EXPECTED_OBJECTS = 3


def load_crop_config():
    if not os.path.exists(CROP_CONFIG_PATH):
        return None
    with open(CROP_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def main():
    from threshold_config import CONFIDENCE_THRESHOLD
    from phy_core.sam3 import PoseEstimator, capture_single_frame
    import pyrealsense2 as rs
    import torch

    # Get intrinsics
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)

    # Init estimator
    estimator = PoseEstimator(device="cuda", confidence_threshold=CONFIDENCE_THRESHOLD)

    # Warmup
    depth_mm, color_bgr = capture_single_frame()
    torch.cuda.synchronize()
    _ = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True)
    torch.cuda.synchronize()

    # Run trials
    all_results = []
    for trial in range(NUM_TRIALS):
        depth_mm, color_bgr = capture_single_frame()
        torch.cuda.synchronize()
        poses = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True)
        torch.cuda.synchronize()

        trial_data = {
            "num_detected": len(poses),
            "poses": [{"x": p.x, "y": p.y, "z": p.z} for p in poses],
        }
        all_results.append(trial_data)

        status = "OK" if len(poses) == EXPECTED_OBJECTS else "MISS"
        sys.stderr.write(f"  Trial {trial+1:2d}: {status} detected={len(poses)}\n")

    # Calculate score
    correct_trials = [r for r in all_results if r["num_detected"] == EXPECTED_OBJECTS]
    detection_rate = len(correct_trials) / NUM_TRIALS

    # Position consistency bonus (only if we have correct trials)
    consistency_bonus = 0.0
    if len(correct_trials) >= 2:
        max_std = 0.0
        for obj_idx in range(EXPECTED_OBJECTS):
            xs = [t["poses"][obj_idx]["x"] for t in correct_trials]
            ys = [t["poses"][obj_idx]["y"] for t in correct_trials]
            zs = [t["poses"][obj_idx]["z"] for t in correct_trials]
            max_std = max(max_std, np.std(xs), np.std(ys), np.std(zs))
        # Bonus: 10 points if max_std < 0.001m, linearly decreasing to 0 at 0.01m
        if max_std < 0.01:
            consistency_bonus = 10.0 * max(0, 1.0 - max_std / 0.01)

    score = detection_rate * 100 + consistency_bonus

    sys.stderr.write(f"\n  threshold={CONFIDENCE_THRESHOLD}\n")
    sys.stderr.write(f"  detection_rate={detection_rate:.0%} ({len(correct_trials)}/{NUM_TRIALS})\n")
    sys.stderr.write(f"  consistency_bonus={consistency_bonus:.1f}\n")
    sys.stderr.write(f"  max_position_std={max_std:.4f}m\n" if len(correct_trials) >= 2 else "")
    sys.stderr.write(f"  SCORE={score:.1f}\n")

    # Output ONLY the score number to stdout
    print(f"{score:.1f}")


if __name__ == "__main__":
    main()
