"""SAM3 segmentation test — capture from RealSense and visualize masks."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sam3"))

import numpy as np
import cv2
import torch
from PIL import Image


def main():
    from capture_realsense import capture_single_frame

    print("=== SAM3 Segmentation Test ===")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    # 1. Capture
    print("\n[1/4] Capturing from RealSense...")
    depth_mm, color_bgr = capture_single_frame()
    print(f"  Color: {color_bgr.shape}, Depth: {depth_mm.shape}")

    # 2. Load model
    print("\n[2/4] Loading SAM3 model...")
    t0 = time.perf_counter()
    from sam3 import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor

    torch.backends.cudnn.benchmark = True
    pt_path = "/tmp/sam3_converted.pt"
    if not os.path.exists(pt_path):
        from safetensors.torch import load_file
        sf_path = os.path.expanduser(
            "~/.cache/huggingface/hub/models--yolain--sam3-safetensors/"
            "snapshots/eb174af94625028887dfe92d2d8483ca5a5d3336/sam3.safetensors"
        )
        state_dict = load_file(sf_path)
        torch.save({"model": state_dict}, pt_path)

    model = build_sam3_image_model(
        device="cuda", eval_mode=True, compile=True,
        load_from_HF=False, checkpoint_path=pt_path,
    )
    processor = Sam3Processor(model, device="cuda", confidence_threshold=0.01)
    print(f"  Loaded in {time.perf_counter() - t0:.1f}s")

    # 3. Run inference
    print("\n[3/4] Running segmentation (prompt='object')...")
    rgb = color_bgr[..., ::-1].copy()
    pil_image = Image.fromarray(rgb)

    # Warmup
    with torch.amp.autocast('cuda', dtype=torch.float16):
        state = processor.set_image(pil_image)
        state = processor.set_text_prompt(prompt="object", state=state)
    torch.cuda.synchronize()

    # Timed run
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    with torch.amp.autocast('cuda', dtype=torch.float16):
        state = processor.set_image(pil_image)
        state = processor.set_text_prompt(prompt="object", state=state)
    torch.cuda.synchronize()
    elapsed = (time.perf_counter() - t0) * 1000

    masks = state.get("masks")
    n_masks = len(masks) if masks is not None else 0
    scores = state.get("scores")

    print(f"  Inference: {elapsed:.1f}ms")
    print(f"  Masks detected: {n_masks}")
    if scores is not None and len(scores) > 0:
        print(f"  Scores: {scores.cpu().numpy().round(3).tolist()}")

    # 4. Visualize
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
        overlay = color_bgr.copy()
        for i in range(n_masks):
            mask_bool = masks_np[i] > 0.5
            c = colors[i % len(colors)]
            overlay[mask_bool] = (overlay[mask_bool] * 0.5 + np.array(c) * 0.5).astype(np.uint8)
            contours, _ = cv2.findContours(
                mask_bool.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(overlay, contours, -1, c, 2)

        cv2.imwrite(os.path.join(out_dir, "02_overlay.png"), overlay)
        print(f"  Saved: {out_dir}/01_input.png, 02_overlay.png")
    else:
        print("  No masks — nothing to visualize.")

    print(f"\n=== RESULT: {n_masks} masks, {elapsed:.1f}ms ===")


if __name__ == "__main__":
    main()
