"""SAM3 Pose estimation repeatability test — 10 trials, 3 objects expected."""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "phy_core"))

import numpy as np
import cv2
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
    from phy_core.sam3 import PoseEstimator, capture_single_frame
    import pyrealsense2 as rs
    import torch

    print(f"=== SAM3 Pose Repeatability Test ({NUM_TRIALS} trials, expect {EXPECTED_OBJECTS} objects) ===\n")

    # 1. Get intrinsics
    print("[Setup] Getting camera intrinsics...")
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)
    print(f"  fx={intr.fx:.1f} fy={intr.fy:.1f} cx={intr.ppx:.1f} cy={intr.ppy:.1f}")

    crop = load_crop_config()
    if crop:
        print(f"  Crop: ({crop[0]},{crop[1]})-({crop[2]},{crop[3]})")

    # 2. Init estimator + warmup
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.008
    print(f"  confidence_threshold={threshold}")
    estimator = PoseEstimator(device="cuda", confidence_threshold=threshold)

    # Warmup with a single capture
    print("[Warmup] Running warmup inference...")
    depth_mm, color_bgr = capture_single_frame()
    torch.cuda.synchronize()
    _ = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True)
    torch.cuda.synchronize()
    print("  Warmup done.\n")

    # 3. Run trials
    all_results = []
    for trial in range(NUM_TRIALS):
        depth_mm, color_bgr = capture_single_frame()
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        poses = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True)
        torch.cuda.synchronize()
        elapsed = (time.perf_counter() - t0) * 1000

        trial_data = {
            "trial": trial + 1,
            "num_detected": len(poses),
            "elapsed_ms": round(elapsed, 1),
            "poses": [],
        }
        for p in poses:
            trial_data["poses"].append({
                "x": round(p.x, 4),
                "y": round(p.y, 4),
                "z": round(p.z, 4),
                "roll": round(p.roll, 1),
                "pitch": round(p.pitch, 1),
                "yaw": round(p.yaw, 1),
            })
        all_results.append(trial_data)

        status = "OK" if len(poses) == EXPECTED_OBJECTS else "MISS"
        poses_str = "  ".join(
            f"[{i}]({p.x:.4f},{p.y:.4f},{p.z:.4f})" for i, p in enumerate(poses)
        )
        print(f"  Trial {trial+1:2d}: {status} detected={len(poses)} time={elapsed:.1f}ms  {poses_str}")

    # 4. Statistics
    print(f"\n{'='*70}")
    print("=== SUMMARY ===")

    detect_counts = [r["num_detected"] for r in all_results]
    times = [r["elapsed_ms"] for r in all_results]
    correct_count = sum(1 for c in detect_counts if c == EXPECTED_OBJECTS)

    print(f"  Detection rate: {correct_count}/{NUM_TRIALS} trials detected exactly {EXPECTED_OBJECTS} objects")
    print(f"  Detection counts: {detect_counts}")
    print(f"  Inference time: mean={np.mean(times):.1f}ms, std={np.std(times):.1f}ms, "
          f"min={np.min(times):.1f}ms, max={np.max(times):.1f}ms")

    # Per-object position statistics (only from trials with correct count)
    correct_trials = [r for r in all_results if r["num_detected"] == EXPECTED_OBJECTS]
    if correct_trials:
        print(f"\n  Position statistics (from {len(correct_trials)} correct trials):")
        for obj_idx in range(EXPECTED_OBJECTS):
            xs = [t["poses"][obj_idx]["x"] for t in correct_trials]
            ys = [t["poses"][obj_idx]["y"] for t in correct_trials]
            zs = [t["poses"][obj_idx]["z"] for t in correct_trials]
            print(f"  [Object {obj_idx}]")
            print(f"    x: mean={np.mean(xs):.4f} std={np.std(xs):.4f} range=[{np.min(xs):.4f}, {np.max(xs):.4f}]")
            print(f"    y: mean={np.mean(ys):.4f} std={np.std(ys):.4f} range=[{np.min(ys):.4f}, {np.max(ys):.4f}]")
            print(f"    z: mean={np.mean(zs):.4f} std={np.std(zs):.4f} range=[{np.min(zs):.4f}, {np.max(zs):.4f}]")

    # Save raw results
    out_path = os.path.join(os.path.dirname(__file__), "output", "repeat_test_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Raw results saved to: {out_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
