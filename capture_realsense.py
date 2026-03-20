import pyrealsense2 as rs
import numpy as np


def capture_single_frame(warmup_frames=5):
    """Capture a single aligned depth + color frame from a RealSense camera.

    Args:
        warmup_frames: Number of frames to discard for auto-exposure stabilization.

    Returns:
        (depth_image, color_image) tuple where:
            depth_image: (480, 640) uint16 numpy array (raw depth values)
            color_image: (480, 640, 3) uint8 numpy array (BGR)
    """
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    align = rs.align(rs.stream.color)

    try:
        pipeline.start(config)

        # Discard initial frames for auto-exposure stabilization
        for _ in range(warmup_frames):
            pipeline.wait_for_frames()

        # Capture and align
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            raise RuntimeError("Failed to capture valid depth and color frames")

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return depth_image, color_image
    finally:
        pipeline.stop()


if __name__ == "__main__":
    depth, color = capture_single_frame()
    print(f"depth_image shape={depth.shape}, dtype={depth.dtype}")
    print(f"color_image shape={color.shape}, dtype={color.dtype}")
