"""RealSense capture utility."""

import pyrealsense2 as rs
import numpy as np


def capture_single_frame(warmup_frames=5):
    """Capture a single aligned depth + color frame from RealSense.

    Returns:
        (depth_image, color_image) tuple:
            depth_image: (480, 640) uint16 numpy array (raw depth in mm)
            color_image: (480, 640, 3) uint8 numpy array (BGR)
    """
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    align = rs.align(rs.stream.color)

    try:
        pipeline.start(config)
        for _ in range(warmup_frames):
            pipeline.wait_for_frames()

        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            raise RuntimeError("Failed to capture valid frames")

        return (
            np.asanyarray(depth_frame.get_data()),
            np.asanyarray(color_frame.get_data()),
        )
    finally:
        pipeline.stop()
