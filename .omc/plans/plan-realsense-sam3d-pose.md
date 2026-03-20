# Implementation Plan: RealSense + SAM 3D Object 6DoF Pose Estimation

## Source Spec
`.omc/specs/deep-interview-realsense-sam3d-pose.md`

## RALPLAN-DR Summary

### Principles
1. **Separation of concerns**: Pose estimation logic is decoupled from camera capture and mask generation
2. **Coordinate convention correctness**: All conversions between PyTorch3D <-> OpenCV frames are explicit, documented, and independently testable
3. **Metric fidelity**: RealSense metric depth (mm) is ground truth for absolute translation. Method B has known limitations due to SSI normalization (documented below)
4. **Comparison-first**: Both methods (hybrid + pointmap) are equal citizens, selectable at runtime
5. **Minimal invasiveness**: No modifications to existing SAM 3D or capture_realsense code

### Decision Drivers
1. **Accuracy for robot pick-and-place**: Translation must be in real-world meters; rotation must be in the correct camera frame
2. **Ease of integration**: Module must be importable, with a clean API that downstream ROS nodes can wrap
3. **Maintainability**: Single file module that wraps existing code without forking or patching SAM 3D internals

### Viable Options

#### Option A: Single-file module with class-based API (CHOSEN)
Create `pose_estimator.py` in workspace root with a `PoseEstimator` class providing two methods.

**Pros:** Simple, single file, direct imports, easy to iterate
**Cons:** All logic in one file; sys.path manipulation needed

#### Option B: Separate package with multiple modules
**Pros:** Better separation of concerns, easier unit testing
**Cons:** Over-engineered for current scope (two methods, one output format)

**Invalidation rationale for Option B:** Scope is well-bounded. Single-file with pure top-level utility functions (per Architect synthesis) provides sufficient testability. Refactoring to package is straightforward if scope grows.

## Requirements Summary
- **Input**: RGB image (np.ndarray, BGR from RealSense — always converted to RGB), depth image (np.uint16, mm), binary mask (np.ndarray, **2D shape H,W**, dtype bool or uint8), camera intrinsics (fx, fy, cx, cy)
- **Output**: `ObjectPose` dataclass with x,y,z (meters) and roll,pitch,yaw (degrees) in standard camera frame (OpenCV: X-right, Y-down, Z-forward)
- Two methods: `hybrid` and `pointmap`
- Importable module with `__main__` block for standalone testing

## Acceptance Criteria
- [ ] `from pose_estimator import PoseEstimator, ObjectPose` works
- [ ] `PoseEstimator(config_path).estimate_pose(rgb, depth, mask, intrinsics, method="hybrid")` returns `ObjectPose`
- [ ] `PoseEstimator(config_path).estimate_pose(rgb, depth, mask, intrinsics, method="pointmap")` returns `ObjectPose`
- [ ] `ObjectPose` has fields: x, y, z (float, meters), roll, pitch, yaw (float, degrees), method (str)
- [ ] Coordinate frame: z forward, x right, y down (OpenCV convention)
- [ ] Handles 640x480 uint16 depth + BGR color from capture_realsense.py
- [ ] Both methods selectable via `method=` parameter
- [ ] `__main__` block captures from RealSense, loads a test mask, runs both methods, prints results
- [ ] Known rotation test: 90-degree Z-rotation in PyTorch3D yields correct RPY in OpenCV frame

## Implementation Steps

### Step 1: Create `ObjectPose` dataclass and utility functions
**File:** `pose_estimator.py` (new, workspace root `/home/robot/jm_ws/pose_estimator.py`)

```python
@dataclass
class ObjectPose:
    x: float      # meters, camera frame (OpenCV)
    y: float      # meters, camera frame (OpenCV)
    z: float      # meters, camera frame (OpenCV)
    roll: float   # degrees
    pitch: float  # degrees
    yaw: float    # degrees
    method: str   # "hybrid" or "pointmap"
```

**Pure utility functions** (top-level, independently testable):

1. `deproject_depth_to_points(depth_mm: np.ndarray, mask: np.ndarray, fx, fy, cx, cy) -> np.ndarray`:
   - Input: depth_mm (H,W) uint16 in mm, mask (H,W) bool, intrinsics
   - Output: (N,3) float64 in meters, standard camera frame (X-right, Y-down, Z-forward)
   - Filters out zero-depth pixels
   - Formula: `X = (u - cx) * Z / fx`, `Y = (v - cy) * Z / fy`, `Z = depth_mm / 1000.0`

2. `compute_centroid(points_3d: np.ndarray) -> tuple[float, float, float]`:
   - Input: (N,3) points in meters
   - Output: (x, y, z) mean position

3. `quaternion_pytorch3d_to_rpy_camera(quat_wxyz: np.ndarray) -> tuple[float, float, float]`:
   - Input: quaternion (w,x,y,z) in PyTorch3D convention
   - Output: (roll, pitch, yaw) in degrees, OpenCV camera frame
   - **Conversion method (conjugation, NOT simple axis negation):**
     ```python
     # PyTorch3D convention: X-left, Y-up, Z-forward
     # OpenCV convention: X-right, Y-down, Z-forward
     # Frame flip matrix F = diag(-1, -1, 1)
     # R_opencv = F @ R_pytorch3d @ F  (conjugation)
     from scipy.spatial.transform import Rotation as R
     R_pt3d = R.from_quat([quat_wxyz[1], quat_wxyz[2], quat_wxyz[3], quat_wxyz[0]])  # scipy uses (x,y,z,w)
     R_mat = R_pt3d.as_matrix()
     F = np.diag([-1, -1, 1])
     R_opencv = F @ R_mat @ F
     rpy = R.from_matrix(R_opencv).as_euler('xyz', degrees=True)
     return (rpy[0], rpy[1], rpy[2])
     ```

4. `depth_to_pointmap(depth_mm: np.ndarray, fx, fy, cx, cy) -> torch.Tensor`:
   - Input: depth_mm (H,W) uint16 in mm, intrinsics
   - Output: torch.Tensor (H,W,3) in meters, standard camera frame
   - Same deprojection as #1 but for full image, returns torch tensor

5. `pointmap_camera_to_pytorch3d(pointmap: torch.Tensor) -> torch.Tensor`:
   - Input: (H,W,3) pointmap in standard camera frame (meters)
   - Output: (H,W,3) pointmap in PyTorch3D convention
   - Applies `camera_to_pytorch3d_camera()` rotation from `inference_pipeline_pointmap.py:26-41`
   - Concretely: negate X and Y channels (`pointmap[..., 0] *= -1; pointmap[..., 1] *= -1`)

6. `validate_inputs(rgb, depth_mm, mask)`:
   - Asserts mask is 2D (H,W), squeezes if (H,W,1)
   - Asserts depth is uint16
   - Asserts rgb shape matches depth spatial dims

### Step 2: Create `PoseEstimator` class
**File:** `pose_estimator.py`

```python
import sys
import os
# Add sam-3d-objects to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sam-3d-objects", "notebook"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sam-3d-objects"))

class PoseEstimator:
    def __init__(self, config_path: str):
        from inference import Inference
        self._inference = Inference(config_path)

    def estimate_pose(self, rgb_or_bgr, depth_mm, mask, intrinsics, method="hybrid", seed=42, is_bgr=True) -> ObjectPose:
        validate_inputs(rgb_or_bgr, depth_mm, mask)
        # Always convert BGR->RGB (capture_realsense outputs BGR)
        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr

        if method == "hybrid":
            return self._estimate_hybrid(rgb, depth_mm, mask, intrinsics, seed)
        elif method == "pointmap":
            return self._estimate_pointmap(rgb, depth_mm, mask, intrinsics, seed)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'hybrid' or 'pointmap'")
```

### Step 3: Implement Method A (Hybrid)
**File:** `pose_estimator.py`, method `_estimate_hybrid`

**Algorithm:**
1. Call `self._inference(rgb, mask, seed=seed)` — uses MoGe internal depth for shape/rotation
2. Extract `output["rotation"]` — quaternion (w,x,y,z) in PyTorch3D camera convention
3. Convert to RPY: `quaternion_pytorch3d_to_rpy_camera(quat)` → (roll, pitch, yaw) degrees in OpenCV frame
4. Deproject depth with mask: `deproject_depth_to_points(depth_mm, mask, *intrinsics)` → (N,3) meters
5. Filter zero-depth, compute centroid → x, y, z in meters (OpenCV frame)
6. Return `ObjectPose(x, y, z, roll, pitch, yaw, method="hybrid")`

**Why this works:** Rotation comes from SAM 3D's learned 3D understanding (MoGe depth + shape model). Translation comes directly from RealSense metric depth — no normalization pipeline, so metric fidelity is guaranteed.

### Step 4: Implement Method B (Pointmap injection)
**File:** `pose_estimator.py`, method `_estimate_pointmap`

**Algorithm:**
1. Convert RealSense depth → pointmap: `depth_to_pointmap(depth_mm, *intrinsics)` → (H,W,3) tensor, meters, camera frame
2. Convert to PyTorch3D convention: `pointmap_camera_to_pytorch3d(pointmap)` → (H,W,3) in PyTorch3D frame
3. **Important:** Pointmap must be 640x480 to match RGB input — no resampling needed since both RealSense streams are 640x480
4. Call `self._inference(rgb, mask, seed=seed, pointmap=pointmap_pytorch3d)`
5. Extract `output["rotation"]` — quaternion in PyTorch3D convention
6. Convert to RPY: `quaternion_pytorch3d_to_rpy_camera(quat)` → same as Method A
7. **Translation:** Use RealSense depth centroid (same as Method A) instead of SAM 3D's SSI-normalized translation. See "Known Limitations" below.
8. Return `ObjectPose(x, y, z, roll, pitch, yaw, method="pointmap")`

**Key decision: Method B uses RealSense depth centroid for translation (same as Method A).** The SAM 3D pose_decoder's translation goes through ScaleShiftInvariant normalization (`pose_target.py:361-372`), introducing systematic scale/shift error. Since we have metric depth from RealSense, using the depth centroid is more reliable for translation. The pointmap injection only improves the **rotation** estimate by giving SAM 3D real metric geometry instead of MoGe's monocular estimate.

**Known Limitations of Method B:**
- SAM 3D's pipeline **infers intrinsics from the pointmap** (`inference_pipeline_pointmap.py:299-308`) instead of using actual RealSense intrinsics. The `Inference.__call__` and `run()` APIs do not accept an intrinsics parameter. This is a known accuracy limitation.
- The pointmap injection path is untested territory — SAM 3D was trained on MoGe pointmaps, not RealSense depth.
- Principle #5 (minimal invasiveness) prevents us from patching the pipeline to accept intrinsics. This is a follow-up improvement.

### Step 5: Implement `__main__` block
**File:** `pose_estimator.py`

```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="6DoF pose estimation with SAM 3D + RealSense")
    parser.add_argument("--config", required=True, help="Path to SAM 3D pipeline.yaml config")
    parser.add_argument("--mask", required=True, help="Path to binary mask image (PNG)")
    parser.add_argument("--fx", type=float, default=None, help="Focal length x (auto-detect if omitted)")
    parser.add_argument("--fy", type=float, default=None, help="Focal length y (auto-detect if omitted)")
    parser.add_argument("--cx", type=float, default=None, help="Principal point x (auto-detect if omitted)")
    parser.add_argument("--cy", type=float, default=None, help="Principal point y (auto-detect if omitted)")
    args = parser.parse_args()

    from capture_realsense import capture_single_frame
    import cv2
    import pyrealsense2 as rs

    # Capture frame
    depth_mm, color_bgr = capture_single_frame()

    # Get intrinsics from RealSense if not provided
    # (preferred: programmatic via rs.pipeline_profile.get_stream().as_video_stream_profile().get_intrinsics())
    intrinsics = (args.fx, args.fy, args.cx, args.cy)

    # Load mask
    mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE) > 0

    # Run both methods
    estimator = PoseEstimator(args.config)
    pose_hybrid = estimator.estimate_pose(color_bgr, depth_mm, mask, intrinsics, method="hybrid")
    pose_pointmap = estimator.estimate_pose(color_bgr, depth_mm, mask, intrinsics, method="pointmap")

    print(f"Hybrid:   {pose_hybrid}")
    print(f"Pointmap: {pose_pointmap}")
```

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Rotation conversion error (PyTorch3D↔OpenCV) | Critical — wrong robot trajectory | Medium | Conjugation formula `R_opencv = F @ R_pt3d @ F` with unit test using known rotation |
| Method B: SAM 3D infers intrinsics from pointmap instead of using RealSense intrinsics | Medium — systematic accuracy degradation | High | Document limitation; use depth centroid for translation; follow-up: patch `Inference.__call__` to accept intrinsics |
| Method B: SAM 3D not trained on RealSense pointmap distribution | Medium — poor rotation estimate | Medium | Method A as fallback; both methods for comparison |
| RealSense depth holes (0 values in mask region) | Medium — centroid skewed | Low | Filter zero-depth pixels in `deproject_depth_to_points` |
| SAM 3D config_path varies by installation | Low — init failure | Medium | `__main__` takes config as required argument; document expected path |
| GPU OOM during SAM 3D inference | Medium — crash | Low | Document GPU requirement; no mitigation needed at module level |

## Verification Steps
1. **Import test**: `python -c "from pose_estimator import PoseEstimator, ObjectPose; print('OK')"`
2. **Rotation unit test**: Create 90-degree rotation about Z-axis in PyTorch3D convention → verify `quaternion_pytorch3d_to_rpy_camera` returns expected RPY in OpenCV frame. Concrete test case:
   - PyTorch3D 90-deg Z-rotation quaternion: `(cos(45°), 0, 0, sin(45°))` = `(0.7071, 0, 0, 0.7071)`
   - Expected OpenCV RPY: `(0, 0, 90)` degrees (yaw only, since Z-axis is shared)
3. **Deprojection test**: Known depth pixel at (320, 240) with depth=500mm, fx=fy=600, cx=320, cy=240 → should yield (0, 0, 0.5) meters
4. **Integration test with RealSense**: Run `__main__` with real captured frame + mask; verify z ≈ measured distance
5. **Compare Method A vs B**: Both should produce similar rotation for the same object

## ADR

### Decision
Single-file `pose_estimator.py` with `PoseEstimator` class, two methods (hybrid/pointmap), pure utility functions at module top-level for testability.

### Drivers
- Robot pick-and-place requires metric pose in camera frame
- Need to compare MoGe-only rotation (Method A) vs RealSense-geometry rotation (Method B)
- Both methods use RealSense depth centroid for translation (metric ground truth)

### Alternatives Considered
1. **Separate package**: Over-engineered for current scope
2. **RealSense pointmap only (no MoGe)**: Loses SAM 3D's learned shape priors
3. **MoGe only (no RealSense depth)**: Cannot provide metric-scale translation
4. **SAM 3D's SSI-normalized translation for Method B**: Rejected because SSI round-trip introduces systematic scale/shift error when given metric pointmaps

### Why Chosen
Single-file balances simplicity with functionality. Both methods use depth centroid for reliable metric translation, differing only in how rotation is estimated (MoGe depth vs RealSense depth via pointmap injection).

### Consequences
- Positive: Clean API, easy to test, no modifications to SAM 3D code
- Positive: Both approaches available for rotation quality comparison
- Positive: Translation is always metric-accurate (from RealSense depth centroid)
- Negative: Method B does not use SAM 3D's translation output (SSI limitation)
- Negative: Method B's rotation accuracy depends on how SAM 3D handles non-MoGe pointmaps

### Follow-ups
- Benchmark both methods with ground-truth poses (e.g., ArUco marker reference)
- Patch `Inference.__call__` to accept intrinsics parameter for Method B accuracy improvement
- Consider ROS wrapper node once preferred method is determined
- Investigate `with_layout_postprocess=True` for potential accuracy improvement

## Changelog (Consensus Improvements Applied)
1. **Fixed rotation conversion**: Replaced vague "negate X/Y axes" with correct conjugation formula `R_opencv = F @ R_pt3d @ F` (Architect finding #1, Critic critical #1)
2. **Documented intrinsics limitation**: Method B's intrinsics are inferred by pipeline, not passed from RealSense (Architect #2, Critic critical #2)
3. **Made BGR→RGB mandatory**: Removed "if needed" qualifier; always convert (Architect #3, Critic major #1)
4. **Method B uses depth centroid for translation**: SSI normalization makes SAM 3D translation unreliable for metric data; use same centroid approach as Method A (Architect #4/#5, Critic major #2)
5. **Added pointmap resolution constraint**: Must be 640x480 to match RGB (Architect #6, Critic major #3)
6. **Enforced 2D mask requirement**: Added validation, documented shape requirement (Architect #7, Critic major #4)
7. **Added concrete rotation unit test**: 90-deg Z-rotation test case with expected values (Critic minor #2)
8. **Noted RealSense intrinsics auto-detection**: `rs.pipeline_profile` as preferred source (Critic minor #3)
9. **Acknowledged Principle #3 tension**: Method B's metric fidelity is limited; documented as known limitation (Critic multi-perspective)
