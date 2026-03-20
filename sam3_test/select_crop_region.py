"""Interactive crop region selector.

Usage:
    python sam3_test/select_crop_region.py              # Use live RealSense capture
    python sam3_test/select_crop_region.py --image PATH # Use existing image

Instructions:
    1. Click two points to define the crop rectangle (top-left, bottom-right)
    2. Press 'r' to reset and re-select
    3. Press 's' to save and exit
    4. Press 'q' to quit without saving

Saves crop config to: crop_config.yaml (workspace root)
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "phy_core"))

import cv2
import yaml
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_config.yaml")
points = []
img_display = None
img_original = None


def mouse_callback(event, x, y, flags, param):
    global points, img_display

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
            img_display = img_original.copy()

            for i, pt in enumerate(points):
                cv2.circle(img_display, pt, 5, (0, 0, 255), -1)
                cv2.putText(img_display, f"P{i+1}({pt[0]},{pt[1]})", (pt[0]+10, pt[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            if len(points) == 2:
                x1 = min(points[0][0], points[1][0])
                y1 = min(points[0][1], points[1][1])
                x2 = max(points[0][0], points[1][0])
                y2 = max(points[0][1], points[1][1])
                cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                w, h = x2 - x1, y2 - y1
                cv2.putText(img_display, f"Crop: ({x1},{y1})-({x2},{y2}) [{w}x{h}]",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(img_display, "Press 's' to save, 'r' to reset, 'q' to quit",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def save_config(points, image_shape):
    x1 = min(points[0][0], points[1][0])
    y1 = min(points[0][1], points[1][1])
    x2 = max(points[0][0], points[1][0])
    y2 = max(points[0][1], points[1][1])

    config = {
        "crop": {
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
            "width": int(x2 - x1),
            "height": int(y2 - y1),
        },
        "original_image_shape": {
            "height": int(image_shape[0]),
            "width": int(image_shape[1]),
        },
    }

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"\nSaved crop config to: {CONFIG_PATH}")
    print(f"  Region: x=[{x1}, {x2}], y=[{y1}, {y2}] ({x2-x1}x{y2-y1})")
    return config


def load_crop_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    c = config["crop"]
    return c["x1"], c["y1"], c["x2"], c["y2"]


def main():
    global points, img_display, img_original

    parser = argparse.ArgumentParser(description="Select crop region interactively")
    parser.add_argument("--image", default=None, help="Path to image (default: live RealSense capture)")
    args = parser.parse_args()

    if args.image:
        img_original = cv2.imread(args.image)
        if img_original is None:
            print(f"ERROR: Cannot read image: {args.image}")
            return
    else:
        from phy_core.sam3 import capture_single_frame
        print("Capturing from RealSense...")
        _, img_original = capture_single_frame()

    print(f"Image: {img_original.shape[1]}x{img_original.shape[0]}")
    print("Click two points to define crop rectangle.")
    print("  's' = save  |  'r' = reset  |  'q' = quit")

    img_display = img_original.copy()

    existing = load_crop_config()
    if existing:
        x1, y1, x2, y2 = existing
        cv2.rectangle(img_display, (x1, y1), (x2, y2), (128, 128, 128), 1)
        cv2.putText(img_display, f"Existing: ({x1},{y1})-({x2},{y2})",
                    (10, img_original.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)

    cv2.namedWindow("Select Crop Region")
    cv2.setMouseCallback("Select Crop Region", mouse_callback)

    while True:
        cv2.imshow("Select Crop Region", img_display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            if len(points) == 2:
                save_config(points, img_original.shape)
                break
            else:
                print("Select 2 points first!")

        elif key == ord("r"):
            points = []
            img_display = img_original.copy()
            if existing:
                x1, y1, x2, y2 = existing
                cv2.rectangle(img_display, (x1, y1), (x2, y2), (128, 128, 128), 1)
            print("Reset. Click two points again.")

        elif key == ord("q"):
            print("Quit without saving.")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
