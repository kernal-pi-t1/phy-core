"""Sweep confidence thresholds to find optimal value.

For each threshold, runs NUM_TRIALS trials and reports detection rate + position consistency.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "phy_core"))

import numpy as np
import yaml

CROP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_config.yaml")
NUM_TRIALS = 10
EXPECTED_OBJECTS = 3

# Thresholds to sweep: coarse then fine
THRESHOLDS = [
    0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008,
    0.010, 0.012, 0.015, 0.020, 0.030, 0.050,
]


def load_crop_config():
    if not os.path.exists(CROP_CONFIG_PATH):
        return None
    with open(CROP_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def run_trials(estimator, intrinsics, num_trials=NUM_TRIALS):
    from phy_core.sam3 import capture_single_frame
    import torch

    results = []
    for _ in range(num_trials):
        depth_mm, color_bgr = capture_single_frame()
        torch.cuda.synchronize()
        poses = estimator.estimate_poses(
            color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True
        )
        torch.cuda.synchronize()
        results.append({
            "num_detected": len(poses),
            "poses": [{"x": p.x, "y": p.y, "z": p.z} for p in poses],
        })
    return results


def calc_score(results):
    correct = [r for r in results if r["num_detected"] == EXPECTED_OBJECTS]
    detection_rate = len(correct) / len(results)

    # Count false positives (detected > expected)
    fp_count = sum(1 for r in results if r["num_detected"] > EXPECTED_OBJECTS)

    consistency_bonus = 0.0
    max_std = float("nan")
    if len(correct) >= 2:
        max_std = 0.0
        for obj_idx in range(EXPECTED_OBJECTS):
            xs = [t["poses"][obj_idx]["x"] for t in correct]
            ys = [t["poses"][obj_idx]["y"] for t in correct]
            zs = [t["poses"][obj_idx]["z"] for t in correct]
            max_std = max(max_std, np.std(xs), np.std(ys), np.std(zs))
        if max_std < 0.01:
            consistency_bonus = 10.0 * max(0, 1.0 - max_std / 0.01)

    score = detection_rate * 100 + consistency_bonus
    return {
        "detection_rate": detection_rate,
        "correct_count": len(correct),
        "fp_count": fp_count,
        "max_std": max_std,
        "consistency_bonus": consistency_bonus,
        "score": score,
    }


def main():
    from phy_core.sam3 import PoseEstimator, capture_single_frame
    import pyrealsense2 as rs
    import torch

    print(f"=== Threshold Sweep ({len(THRESHOLDS)} values, {NUM_TRIALS} trials each) ===\n")

    # Get intrinsics
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)

    all_sweep_results = []

    for i, threshold in enumerate(THRESHOLDS):
        print(f"[{i+1}/{len(THRESHOLDS)}] threshold={threshold:.4f} ...", end=" ", flush=True)

        estimator = PoseEstimator(device="cuda", confidence_threshold=threshold)

        # Warmup
        depth_mm, color_bgr = capture_single_frame()
        torch.cuda.synchronize()
        _ = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt="object", is_bgr=True)
        torch.cuda.synchronize()

        # Run trials
        t0 = time.perf_counter()
        results = run_trials(estimator, intrinsics, NUM_TRIALS)
        elapsed = time.perf_counter() - t0

        stats = calc_score(results)
        stats["threshold"] = threshold
        stats["elapsed_s"] = round(elapsed, 1)
        all_sweep_results.append(stats)

        det_str = f"{stats['correct_count']}/{NUM_TRIALS}"
        fp_str = f" FP={stats['fp_count']}" if stats['fp_count'] > 0 else ""
        std_str = f" max_std={stats['max_std']:.4f}m" if not np.isnan(stats['max_std']) else ""
        print(f"detect={det_str}{fp_str}{std_str}  SCORE={stats['score']:.1f}  ({elapsed:.1f}s)")

        # Free GPU memory
        del estimator
        torch.cuda.empty_cache()

    # Summary table
    print(f"\n{'='*80}")
    print(f"{'Threshold':>10} {'Detect':>8} {'FP':>4} {'MaxStd(mm)':>11} {'Bonus':>6} {'SCORE':>7}")
    print(f"{'-'*10} {'-'*8} {'-'*4} {'-'*11} {'-'*6} {'-'*7}")

    best = max(all_sweep_results, key=lambda r: r["score"])
    for r in all_sweep_results:
        marker = " <-- BEST" if r["threshold"] == best["threshold"] else ""
        std_str = f"{r['max_std']*1000:.2f}" if not np.isnan(r['max_std']) else "N/A"
        print(f"{r['threshold']:>10.4f} {r['correct_count']:>5}/{NUM_TRIALS} {r['fp_count']:>4} "
              f"{std_str:>11} {r['consistency_bonus']:>6.1f} {r['score']:>7.1f}{marker}")

    print(f"\nBEST: threshold={best['threshold']} score={best['score']:.1f} "
          f"(detect={best['correct_count']}/{NUM_TRIALS}, FP={best['fp_count']})")

    # Save raw results
    out_path = os.path.join(os.path.dirname(__file__), "output", "sweep_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_sweep_results, f, indent=2, default=str)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()
