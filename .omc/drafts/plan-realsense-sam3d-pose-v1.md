# Implementation Plan: RealSense + SAM 3D Object 6DoF Pose Estimation

## Source Spec
`.omc/specs/deep-interview-realsense-sam3d-pose.md`

## RALPLAN-DR Summary

### Principles
1. **Separation of concerns**: Pose estimation logic is decoupled from camera capture and mask generation
2. **Coordinate convention correctness**: All conversions between PyTorch3D ↔ OpenCV/standard camera frames are explicit and tested
3. **Metric fidelity**: RealSense metric depth (mm) is the ground truth for absolute translation; SAM 3D provides relative geometry
4. **Comparison-first**: Both methods (hybrid + pointmap) are equal citizens, selectable at runtime
5. **Minimal invasiveness**: No modifications to existing SAM 3D or capture_realsense code

### Decision Drivers
1. **Accuracy for robot pick-and-place**: Translation must be in real-world meters; rotation must be in the correct camera frame
2. **Ease of integration**: Module must be importable, with a clean API that downstream ROS nodes can wrap
3. **Maintainability**: Single file module that wraps existing code without forking or patching SAM 3D internals

### Viable Options

#### Option A: Single-file module with class-based API (CHOSEN)
Create `pose_estimator.py` in workspace root with a `PoseEstimator` class that wraps SAM 3D `Inference` and provides two methods.

**Pros:**
- Simple, single file, no package structure needed
- Direct imports of existing code
- Easy to test and iterate

**Cons:**
- All logic in one file could grow complex
- sys.path manipulation needed for sam-3d-objects imports

#### Option B: Separate package with multiple modules
Create a `pose_estimation/` package with separate modules for deprojection, coordinate conversion, and inference.

**Pros:**
- Better separation of concerns
- Easier unit testing of individual components

**Cons:**
- Over-engineered for current scope (single use case, two methods)
- More files to maintain
- More complex imports

**Invalidation rationale for Option B:** The scope is well-bounded (two methods, one output format). A single-file module with clear internal functions provides sufficient organization without the overhead of a package structure. If the module grows beyond ~300 lines, refactoring into a package is straightforward.

## Requirements Summary
- Input: RGB image (np.ndarray), depth image (np.uint16, mm), binary mask (np.ndarray), camera intrinsics (fx, fy, cx, cy)
- Output: `ObjectPose` dataclass with x,y,z (meters) and roll,pitch,yaw (degrees) in standard camera frame
- Two methods: `hybrid` (SAM 3D rotation + RealSense depth centroid) and `pointmap` (RealSense pointmap injected into SAM 3D)
- Importable module with `__main__` block for standalone testing

## Acceptance Criteria
- [ ] `from pose_estimator import PoseEstimator, ObjectPose` works
- [ ] `PoseEstimator(config_path).estimate_pose(rgb, depth, mask, intrinsics, method="hybrid")` returns `ObjectPose`
- [ ] `PoseEstimator(config_path).estimate_pose(rgb, depth, mask, intrinsics, method="pointmap")` returns `ObjectPose`
- [ ] `ObjectPose` has fields: x, y, z (float, meters), roll, pitch, yaw (float, degrees), method (str)
- [ ] Coordinate frame: z forward, x right, y down (OpenCV/standard camera convention)
- [ ] Handles 640x480 uint16 depth + BGR color from capture_realsense.py
- [ ] `__main__` block captures from RealSense, loads a test mask, runs both methods, prints results
- [ ] PyTorch3D→OpenCV quaternion conversion is correct (validated by known rotation)

## Implementation Steps

### Step 1: Create `ObjectPose` dataclass and utility functions
**File:** `pose_estimator.py` (new, workspace root)

```python
@dataclass
class ObjectPose:
    x: float      # meters, camera frame
    y: float      # meters, camera frame
    z: float      # meters, camera frame
    roll: float   # degrees
    pitch: float  # degrees
    yaw: float    # degrees
    method: str   # "hybrid" or "pointmap"
```

Utility functions:
- `deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy) -> np.ndarray (N,3)`: Deproject masked depth pixels to 3D points in camera frame (meters)
- `compute_centroid(points_3d) -> (x, y, z)`: Mean of valid (non-zero depth) 3D points
- `quaternion_pytorch3d_to_rpy_camera(quat_wxyz) -> (roll, pitch, yaw)`: Convert PyTorch3D quaternion to RPY in standard camera frame
  - PyTorch3D convention: X-left, Y-up, Z-into-screen
  - Standard camera: X-right, Y-down, Z-forward
  - Conversion: negate X and Y axes of the rotation, then extract euler angles
  - Uses `scipy.spatial.transform.Rotation`
- `depth_to_pointmap(depth_mm, fx, fy, cx, cy) -> torch.Tensor (H,W,3)`: Convert full depth image to pointmap in camera frame (meters)

### Step 2: Create `PoseEstimator` class
**File:** `pose_estimator.py`

```python
class PoseEstimator:
    def __init__(self, config_path: str):
        # Add sam-3d-objects to sys.path
        # Initialize SAM 3D Inference(config_path)
        self._inference = Inference(config_path)

    def estimate_pose(self, rgb, depth_mm, mask, intrinsics, method="hybrid", seed=42) -> ObjectPose:
        if method == "hybrid":
            return self._estimate_hybrid(rgb, depth_mm, mask, intrinsics, seed)
        elif method == "pointmap":
            return self._estimate_pointmap(rgb, depth_mm, mask, intrinsics, seed)
```

### Step 3: Implement Method A (Hybrid)
**File:** `pose_estimator.py`, method `_estimate_hybrid`

1. Convert BGR→RGB if needed
2. Call `self._inference(rgb, mask, seed=seed)` — uses MoGe internal depth
3. Extract `output["rotation"]` (quaternion, PyTorch3D convention w,x,y,z)
4. Convert quaternion to RPY in camera frame via `quaternion_pytorch3d_to_rpy_camera()`
5. Deproject depth with mask: `deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)`
6. Compute centroid → x, y, z in meters
7. Return `ObjectPose(x, y, z, roll, pitch, yaw, method="hybrid")`

**Key coordinate conversion detail:**
- `pose_decoder` returns `instance_quaternion_l2c` in PyTorch3D camera space
- PyTorch3D: X-left, Y-up, Z-forward (looking at screen)
- Standard camera (OpenCV): X-right, Y-down, Z-forward
- The `flip_coords_pytorch3d_to_opencv` function (layout_post_optimization_utils.py:1148) shows: negate X and Y
- For rotation: apply the flip transform (diag(-1,-1,1)) to the rotation matrix before extracting euler angles

### Step 4: Implement Method B (Pointmap injection)
**File:** `pose_estimator.py`, method `_estimate_pointmap`

1. Convert RealSense depth → pointmap: `depth_to_pointmap(depth_mm, fx, fy, cx, cy)` → (H,W,3) tensor in meters, camera frame
2. Apply `camera_to_pytorch3d_camera()` rotation to convert camera→PyTorch3D convention (inference_pipeline_pointmap.py:26-41)
3. Call `self._inference(rgb, mask, seed=seed, pointmap=pointmap_pytorch3d)`
4. Extract `output["rotation"]` and `output["translation"]`
5. Convert rotation: quaternion_pytorch3d_to_rpy_camera()
6. Convert translation: apply inverse of camera_to_pytorch3d_camera to get back to standard camera frame, scale to meters
7. Return `ObjectPose(x, y, z, roll, pitch, yaw, method="pointmap")`

**Critical:** The pointmap passed to SAM 3D must be in PyTorch3D convention (same as MoGe output). `camera_to_pytorch3d_camera()` at inference_pipeline_pointmap.py:26-41 defines this transform as `look_at_view_transform(eye=[0,0,-1], at=[0,0,0], up=[0,-1,0])`.

### Step 5: Implement `__main__` block
**File:** `pose_estimator.py`

```python
if __name__ == "__main__":
    from capture_realsense import capture_single_frame
    import cv2

    depth_mm, color_bgr = capture_single_frame()
    # Load test mask (user provides path via argparse)
    mask = load_mask(args.mask_path)
    intrinsics = (fx, fy, cx, cy)  # from argparse or hardcoded RealSense defaults

    estimator = PoseEstimator(args.config_path)

    pose_hybrid = estimator.estimate_pose(color_bgr, depth_mm, mask, intrinsics, method="hybrid")
    pose_pointmap = estimator.estimate_pose(color_bgr, depth_mm, mask, intrinsics, method="pointmap")

    print(f"Hybrid:   {pose_hybrid}")
    print(f"Pointmap: {pose_pointmap}")
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SAM 3D model not trained on RealSense pointmap distribution | Method B may produce poor pose estimates | Method A (hybrid) as fallback; both methods available for comparison |
| PyTorch3D↔OpenCV coordinate conversion error | Incorrect rotation output | Explicit conversion with known test case; flip_coords_pytorch3d_to_opencv as reference |
| RealSense depth holes (0 values in mask region) | Centroid calculation skewed | Filter out zero-depth pixels before centroid computation |
| SAM 3D config_path varies by installation | Init failure | Document required config path; `__main__` takes it as argument |
| MoGe relative scale vs. RealSense metric scale | Translation in Method B may not be in meters | Method B translation needs scale calibration; document limitation |

## Verification Steps
1. Import test: `python -c "from pose_estimator import PoseEstimator, ObjectPose; print('OK')"`
2. Unit test coordinate conversion: Create known rotation matrix, verify RPY output
3. Integration test with RealSense: Run `__main__` block with a real captured frame + mask
4. Sanity check: Object at ~0.5m distance should report z ≈ 0.5 in Method A
5. Compare Method A vs B: Both should produce similar rotation for the same object

## ADR

### Decision
Single-file `pose_estimator.py` module with `PoseEstimator` class providing two methods (hybrid, pointmap).

### Drivers
- Robot pick-and-place requires metric-accurate pose in camera frame
- Need to compare MoGe-only vs. RealSense-depth approaches
- Module must integrate into larger ROS-based system via import

### Alternatives Considered
1. **Separate package**: Over-engineered for current scope
2. **RealSense pointmap only (no MoGe)**: Loses SAM 3D's learned shape priors
3. **MoGe only (no RealSense depth)**: Cannot provide metric-scale translation

### Why Chosen
Single-file approach balances simplicity with functionality. Both methods are implemented as equal citizens, letting the user empirically determine which works better for their specific objects and setup.

### Consequences
- Positive: Clean API, easy to test, no modifications to SAM 3D code
- Positive: Both approaches available for A/B comparison
- Negative: Method B's accuracy depends on how well SAM 3D handles non-MoGe pointmaps (untested territory)
- Negative: Single file may need refactoring if scope grows significantly

### Follow-ups
- Benchmark both methods with ground-truth poses (e.g., ArUco marker reference)
- Consider ROS wrapper node once preferred method is determined
- Investigate whether layout post-optimization improves results with RealSense pointmap
