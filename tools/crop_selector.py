#!/usr/bin/env python3
"""Interactive crop region selector using RealSense camera.

Usage:
    python3 tools/crop_selector.py

Controls:
    - Click two points to define crop box (top-left, bottom-right)
    - 'r' : Reset selection
    - 's' : Save to crop_config.yaml
    - 'q' / ESC : Quit
"""

import os
import sys
import cv2
import numpy as np
import yaml

CROP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_config.yaml")
WAYPOINTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "phy_core", "config", "waypoints.yaml"
)

points = []
current_frame = None


def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
            print(f"Point {len(points)}: ({x}, {y})")


def draw_overlay(frame):
    display = frame.copy()
    h, w = display.shape[:2]

    # Load intrinsics from waypoints.yaml
    fx, fy, cx, cy = load_intrinsics()
    info = f"Image: {w}x{h}  fx={fx:.1f} fy={fy:.1f} cx={cx:.1f} cy={cy:.1f}"
    cv2.putText(display, info, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    # Draw crosshair at principal point
    cv2.drawMarker(display, (int(cx), int(cy)), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)

    # Draw clicked points
    for i, pt in enumerate(points):
        color = (0, 0, 255) if i == 0 else (255, 0, 0)
        cv2.circle(display, pt, 5, color, -1)
        cv2.putText(display, f"P{i+1}({pt[0]},{pt[1]})", (pt[0]+8, pt[1]-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    # Draw box if two points selected
    if len(points) == 2:
        x1 = min(points[0][0], points[1][0])
        y1 = min(points[0][1], points[1][1])
        x2 = max(points[0][0], points[1][0])
        y2 = max(points[0][1], points[1][1])
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        box_info = f"Crop: ({x1},{y1})-({x2},{y2})  {x2-x1}x{y2-y1}"
        cv2.putText(display, box_info, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        cv2.putText(display, "'s'=Save  'r'=Reset  'q'=Quit", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    else:
        msg = f"Click {2 - len(points)} point(s) to define crop box"
        cv2.putText(display, msg, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

    return display


def load_intrinsics():
    """Load camera intrinsics from waypoints.yaml."""
    try:
        with open(WAYPOINTS_PATH, "r") as f:
            config = yaml.safe_load(f)
        params = config["sam3_node"]["ros__parameters"]
        return params["fx"], params["fy"], params["cx"], params["cy"]
    except Exception:
        return 615.0, 615.0, 320.0, 240.0


def save_crop_config(x1, y1, x2, y2, img_h, img_w):
    config = {
        "crop": {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": x2 - x1,
            "height": y2 - y1,
        },
        "original_image_shape": {
            "width": img_w,
            "height": img_h,
        },
    }
    with open(CROP_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Saved crop config to {CROP_CONFIG_PATH}")
    print(f"  Region: ({x1},{y1})-({x2},{y2})  Size: {x2-x1}x{y2-y1}")


def run_with_realsense():
    """Live RealSense camera mode."""
    import pyrealsense2 as rs

    global points, current_frame

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    cv2.namedWindow("Crop Selector")
    cv2.setMouseCallback("Crop Selector", mouse_callback)

    print("=== Crop Region Selector ===")
    print("Click 2 points to define crop box.")
    print("'s'=Save  'r'=Reset  'q'=Quit")

    try:
        for _ in range(10):  # warmup
            pipeline.wait_for_frames()

        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            current_frame = np.asanyarray(color_frame.get_data())
            display = draw_overlay(current_frame)
            cv2.imshow("Crop Selector", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('r'):
                points = []
                print("Reset.")
            elif key == ord('s') and len(points) == 2:
                h, w = current_frame.shape[:2]
                x1 = min(points[0][0], points[1][0])
                y1 = min(points[0][1], points[1][1])
                x2 = max(points[0][0], points[1][0])
                y2 = max(points[0][1], points[1][1])
                save_crop_config(x1, y1, x2, y2, h, w)
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


def run_with_image(image_path):
    """Static image mode (for testing without camera)."""
    global points, current_frame

    current_frame = cv2.imread(image_path)
    if current_frame is None:
        print(f"Error: Cannot read image '{image_path}'")
        sys.exit(1)

    cv2.namedWindow("Crop Selector")
    cv2.setMouseCallback("Crop Selector", mouse_callback)

    print(f"=== Crop Selector (image: {image_path}) ===")
    print("Click 2 points to define crop box.")

    while True:
        display = draw_overlay(current_frame)
        cv2.imshow("Crop Selector", display)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            points = []
            print("Reset.")
        elif key == ord('s') and len(points) == 2:
            h, w = current_frame.shape[:2]
            x1 = min(points[0][0], points[1][0])
            y1 = min(points[0][1], points[1][1])
            x2 = max(points[0][0], points[1][0])
            y2 = max(points[0][1], points[1][1])
            save_crop_config(x1, y1, x2, y2, h, w)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_with_image(sys.argv[1])
    else:
        run_with_realsense()
