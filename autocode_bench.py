"""Autocode benchmark: measure SAM3 inference speed with fixed image."""

import sys
import os
import time
import json

import numpy as np
import torch
import cv2
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sam3"))

BENCHMARK_IMAGE = os.path.join(os.path.dirname(__file__), ".autocode", "benchmark_input.png")
SAFETENSORS_PATH = os.path.expanduser(
    "~/.cache/huggingface/hub/models--yolain--sam3-safetensors/snapshots/eb174af94625028887dfe92d2d8483ca5a5d3336/sam3.safetensors"
)


def convert_safetensors_to_pt(safetensors_path, pt_path):
    from safetensors.torch import load_file
    state_dict = load_file(safetensors_path)
    torch.save({"model": state_dict}, pt_path)
    return pt_path


def load_model(device):
    bpe_path = os.path.join(os.path.dirname(__file__), "sam3", "sam3", "assets", "bpe_simple_vocab_16e6.txt.gz")
    pt_path = "/tmp/sam3_converted.pt"
    if not os.path.exists(pt_path):
        convert_safetensors_to_pt(SAFETENSORS_PATH, pt_path)

    from sam3 import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor
    model = build_sam3_image_model(
        bpe_path=bpe_path, device=device, eval_mode=True,
        load_from_HF=False, checkpoint_path=pt_path,
    )
    processor = Sam3Processor(model, device=device, confidence_threshold=0.01)
    return processor


def run_benchmark(processor, image_path, n_runs=5, prompt="object"):
    """Run inference benchmark. Returns avg time in ms and mask count."""
    color_bgr = cv2.imread(image_path)
    rgb = color_bgr[..., ::-1].copy()
    pil_image = Image.fromarray(rgb)
    device = processor.device

    # Warmup
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    state = processor.set_image(pil_image)
    state = processor.set_text_prompt(prompt=prompt, state=state)
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # Timed runs
    times = []
    for _ in range(n_runs):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        state = processor.set_image(pil_image)
        state = processor.set_text_prompt(prompt=prompt, state=state)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        times.append(time.perf_counter() - t0)

    avg_ms = np.mean(times) * 1000
    masks = state.get("masks")
    n_masks = len(masks) if masks is not None else 0

    return avg_ms, n_masks


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = load_model(device)
    avg_ms, n_masks = run_benchmark(processor, BENCHMARK_IMAGE)

    # Output metric as JSON for easy parsing
    result = {"avg_ms": round(avg_ms, 2), "n_masks": n_masks}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
