"""SAM3 segmentation test — uses Sam3FastProcessor (same as sam3_node).

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
    from phy_core.sam3 import Sam3FastProcessor, capture_single_frame
    import pyrealsense2 as rs

    print("=== SAM3 Segmentation Test (Sam3FastProcessor) ===")

    # 1. Get intrinsics
    print("\n[1/4] Getting camera intrinsics...")
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipe.start(cfg)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipe.stop()
    print(f"  fx={intr.fx:.1f} fy={intr.fy:.1f} cx={intr.ppx:.1f} cy={intr.ppy:.1f}")

    # 2. Capture
    print("\n[2/4] Capturing from RealSense...")
    depth_mm, color_bgr = capture_single_frame()
    print(f"  Color: {color_bgr.shape}, Depth: {depth_mm.shape}")

    # 3. Apply crop_config
    crop = load_crop_config()
    if crop:
        x1, y1, x2, y2 = crop
        print(f"  Crop config: ({x1},{y1})-({x2},{y2}) [{x2-x1}x{y2-y1}]")
        color_cropped = color_bgr[y1:y2, x1:x2].copy()
    else:
        print("  No crop_config.yaml — using full frame")
        color_cropped = color_bgr

    # 4. Run segmentation via Sam3FastProcessor
    print("\n[3/4] Loading Sam3FastProcessor & running segmentation...")
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
    print(f"  confidence_threshold={threshold}")
    processor = Sam3FastProcessor(device="cuda", confidence_threshold=threshold)

    from PIL import Image
    import torch

    rgb = color_cropped[..., ::-1].copy()
    pil_image = Image.fromarray(rgb)

    # Warmup
    torch.cuda.synchronize()
    _ = processor.segment(pil_image, prompt="object")
    torch.cuda.synchronize()

    # Timed run
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    state = processor.segment(pil_image, prompt="object")
    torch.cuda.synchronize()
    elapsed = (time.perf_counter() - t0) * 1000

    masks = state.get("masks")
    n_masks = len(masks) if masks is not None else 0
    scores = state.get("scores")

    print(f"  Inference: {elapsed:.1f}ms")
    print(f"  Masks detected: {n_masks}")
    if scores is not None and len(scores) > 0:
        print(f"  Scores: {scores.cpu().numpy().round(3).tolist()}")

    # 5. Visualize
    print("\n[4/4] Saving visualization...")
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    cv2.imwrite(os.path.join(out_dir, "01_input.png"), color_bgr)

    if masks is not None and n_masks > 0:
        masks_np = masks.squeeze(1).cpu().numpy()
        colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255),
            (255, 255, 0), (0, 255, 255), (255, 0, 255),
        ]

        # Overlay on cropped image
        overlay_crop = color_cropped.copy()
        for i in range(n_masks):
            mask_bool = masks_np[i] > 0.5
            c = colors[i % len(colors)]
            overlay_crop[mask_bool] = (overlay_crop[mask_bool] * 0.5 + np.array(c) * 0.5).astype(np.uint8)
            contours, _ = cv2.findContours(
                mask_bool.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(overlay_crop, contours, -1, c, 2)

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

        cv2.imwrite(os.path.join(out_dir, "02_overlay_crop.png"), overlay_crop)
        cv2.imwrite(os.path.join(out_dir, "03_overlay_full.png"), overlay_full)
        print(f"  Saved: {out_dir}/01_input.png, 02_overlay_crop.png, 03_overlay_full.png")
    else:
        # No masks — still save and show the input image
        cv2.imwrite(os.path.join(out_dir, "02_overlay_crop.png"), color_cropped)
        overlay_full = color_bgr.copy()
        if crop:
            x1, y1, x2, y2 = crop
            cv2.rectangle(overlay_full, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(overlay_full, f"crop ({x1},{y1})-({x2},{y2}) - NO MASKS",
                        (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite(os.path.join(out_dir, "03_overlay_full.png"), overlay_full)
        print(f"  No masks detected. Saved input images to {out_dir}/")

    # Show result on screen (use subprocess to avoid GTK issues)
    show_path = os.path.join(out_dir, "03_overlay_full.png")
    if os.path.exists(show_path):
        import subprocess
        print(f"\nOpening: {show_path}")
        subprocess.Popen(["eog", show_path], env={**os.environ, "DISPLAY": ":0"})

    print(f"\n=== RESULT: {n_masks} masks, {elapsed:.1f}ms ===")


if __name__ == "__main__":
    main()
