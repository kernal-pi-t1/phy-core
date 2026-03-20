"""SAM3 segmentation with visualization output."""

import sys
import os
import time

import numpy as np
import torch
import cv2
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sam3"))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
SAFETENSORS_PATH = os.path.expanduser(
    "~/.cache/huggingface/hub/models--yolain--sam3-safetensors/snapshots/eb174af94625028887dfe92d2d8483ca5a5d3336/sam3.safetensors"
)


def convert_safetensors_to_pt(safetensors_path, pt_path):
    """Convert safetensors to .pt checkpoint format expected by model_builder."""
    from safetensors.torch import load_file
    state_dict = load_file(safetensors_path)
    torch.save({"model": state_dict}, pt_path)
    return pt_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        torch.cuda.reset_peak_memory_stats()

    # --- 1. Capture ---
    from capture_realsense import capture_single_frame
    depth_mm, color_bgr = capture_single_frame()
    print(f"Captured: {color_bgr.shape}")

    # Save input
    cv2.imwrite(os.path.join(OUTPUT_DIR, "01_input.png"), color_bgr)
    print(f"Saved: output/01_input.png")

    # --- 2. Convert safetensors → pt ---
    pt_path = "/tmp/sam3_converted.pt"
    if not os.path.exists(pt_path):
        print("Converting safetensors → pt...")
        convert_safetensors_to_pt(SAFETENSORS_PATH, pt_path)
        print(f"Converted: {pt_path}")

    # --- 3. Load SAM3 model with checkpoint ---
    bpe_path = os.path.join(os.path.dirname(__file__), "sam3", "sam3", "assets", "bpe_simple_vocab_16e6.txt.gz")

    t0 = time.perf_counter()
    from sam3 import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor
    model = build_sam3_image_model(
        bpe_path=bpe_path, device=device, eval_mode=True,
        load_from_HF=False, checkpoint_path=pt_path,
    )
    processor = Sam3Processor(model, device=device, confidence_threshold=0.01)
    t_load = time.perf_counter() - t0
    print(f"\nModel loaded: {t_load:.1f}s")

    # --- 4. Run segmentation ---
    rgb = color_bgr[..., ::-1].copy()
    pil_image = Image.fromarray(rgb)

    # Warmup
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    state = processor.set_image(pil_image)
    state = processor.set_text_prompt(prompt="object", state=state)
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # Timed run
    N = 3
    times = []
    for _ in range(N):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        state = processor.set_image(pil_image)
        state = processor.set_text_prompt(prompt="object", state=state)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        times.append(time.perf_counter() - t0)

    avg_t = np.mean(times) * 1000
    masks = state.get("masks")
    n_masks = len(masks) if masks is not None else 0
    print(f"\nSAM3 inference: {avg_t:.1f} ms (avg {N} runs)")
    print(f"Masks detected: {n_masks}")

    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 1e6
        print(f"GPU peak: {peak:.1f} MB")

    # --- 5. Save outputs ---
    if masks is not None and n_masks > 0:
        masks_np = masks.squeeze(1).cpu().numpy()  # (N, H, W)

        # Color palette for different masks
        colors = [
            (0, 255, 0),    # green
            (255, 0, 0),    # blue
            (0, 0, 255),    # red
            (255, 255, 0),  # cyan
            (0, 255, 255),  # yellow
            (255, 0, 255),  # magenta
        ]

        # Overlay all masks on input
        overlay = color_bgr.copy()
        for i in range(n_masks):
            mask_bool = masks_np[i] > 0.5
            color = colors[i % len(colors)]
            # Semi-transparent overlay
            overlay[mask_bool] = (
                overlay[mask_bool] * 0.5 + np.array(color) * 0.5
            ).astype(np.uint8)
            # Contour
            contours, _ = cv2.findContours(
                mask_bool.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(overlay, contours, -1, color, 2)

            # Save individual mask
            mask_vis = (mask_bool * 255).astype(np.uint8)
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"03_mask_{i:02d}.png"), mask_vis)

        cv2.imwrite(os.path.join(OUTPUT_DIR, "02_segmentation_overlay.png"), overlay)
        print(f"\nSaved {n_masks + 2} files to output/:")
        print(f"  01_input.png")
        print(f"  02_segmentation_overlay.png")
        for i in range(n_masks):
            print(f"  03_mask_{i:02d}.png")
    else:
        print("\nNo masks detected — nothing to visualize.")

    # nvidia-smi
    os.system("nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader")


if __name__ == "__main__":
    main()
