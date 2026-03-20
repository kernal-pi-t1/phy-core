# Plan: SAM 3 Mask + RealSense Depth PCA 6DoF Pose Estimation

## Source Spec
- `/home/robot/jm_ws/.omc/specs/deep-interview-sam3-pca-pose.md`

## Requirements Summary
Replace existing `pose_estimator.py` (SAM 3D Objects) with a new pipeline:
1. SAM 3 text-prompt segmentation → N object masks
2. Per-mask: RealSense depth deprojection → 3D point cloud
3. PCA on point cloud → rotation matrix + gravity correction (Y-down)
4. Centroid → translation (x, y, z meters)
5. Output: `List[ObjectPose]` with 6DoF per object

## RALPLAN-DR Summary

### Principles
1. **Simplicity over generality**: PCA + gravity is intentionally simple; avoid over-engineering rotation estimation
2. **Reuse existing utilities**: Keep `deproject_depth_to_points()`, `compute_centroid()`, `validate_inputs()`, `ObjectPose` dataclass
3. **Clean dependency cut**: Fully remove SAM 3D Objects imports; no backward compatibility shims
4. **Text-prompt segmentation**: SAM 3 requires text prompts (not auto-mask-generator); design the API around configurable text prompts
5. **Deterministic orientation**: PCA eigenvectors have sign ambiguity; gravity correction resolves this for tabletop pick-and-place

### Decision Drivers
1. **SAM 3 API constraint**: SAM 3 uses `set_text_prompt(prompt)` not auto-mask-generator — the module must accept text prompts to specify what to segment
2. **PCA sign ambiguity**: PCA eigenvectors can flip 180°; gravity vector (Y-down in camera frame) provides a consistent reference to resolve this
3. **Multi-object output**: Current `pose_estimator.py` returns a single `ObjectPose`; new pipeline must return `List[ObjectPose]` for all segmented objects

### Viable Options

#### Option A: Monolithic PoseEstimator class (Recommended)
- Single class wraps SAM 3 model loading + PCA pose estimation
- `__init__` loads SAM 3 model once; `estimate_poses(rgb, depth, intrinsics, prompt)` returns `List[ObjectPose]`
- **Pros**: Simple API, single import, model loaded once
- **Cons**: Less modular, harder to swap segmentation backend later

#### Option B: Separate Segmentor + PoseEstimator
- `Sam3Segmentor` class for mask generation, separate `PcaPoseEstimator` for pose
- Compose: `masks = segmentor.segment(rgb, prompt)` → `poses = estimator.estimate(depth, masks, intrinsics)`
- **Pros**: More modular, can swap segmentor independently
- **Cons**: More complex API, two classes to manage, user must handle composition

**Invalidation of Option B**: For the current scope (single pipeline, no planned backend swaps), the extra abstraction adds complexity without benefit. The user explicitly chose to replace SAM 3D Objects entirely, not build a pluggable system.

## Acceptance Criteria
- [ ] `pose_estimator.py` fully replaced with SAM 3 + PCA implementation
- [ ] No imports from `sam-3d-objects/` remain
- [ ] `from pose_estimator import PoseEstimator, ObjectPose` works
- [ ] `PoseEstimator.__init__(device="cuda")` loads SAM 3 model
- [ ] `estimate_poses(rgb_bgr, depth_mm, intrinsics, prompt="object")` returns `List[ObjectPose]`
- [ ] Each `ObjectPose` has x,y,z (meters), roll,pitch,yaw (degrees) in OpenCV camera frame
- [ ] PCA rotation matrix has det(R)=1 (right-hand rule enforced)
- [ ] Gravity correction aligns Y-axis with camera Y-down
- [ ] `__main__` block captures from RealSense, runs SAM 3 segmentation, prints all poses
- [ ] Works with 640x480 RealSense input (uint16 depth, BGR color)

## Implementation Steps

### Step 1: Understand SAM 3 API (no code changes)
- Read `sam3/sam3/model/sam3_image_processor.py` for `Sam3Processor` API
- Read `sam3/sam3/model_builder.py` for `build_sam3_image_model()`
- Verify model loading and text-prompt inference work

### Step 2: Rewrite `pose_estimator.py`

**Keep unchanged:**
- `ObjectPose` dataclass (line 38-47)
- `validate_inputs()` (line 54-72) — modify to make mask optional (auto-segmentation generates masks)
- `deproject_depth_to_points()` (line 75-104)
- `compute_centroid()` (line 107-119)

**Remove entirely:**
- Lines 19-20: `sys.path.insert` for sam-3d-objects
- Lines 28-31: sam-3d-objects path setup
- `quaternion_pytorch3d_to_rpy_camera()` (line 122-156)
- `depth_to_pointmap()` (line 159-186)
- `pointmap_camera_to_pytorch3d()` (line 189-208)
- `PoseEstimator.__init__` with SAM 3D `Inference` (line 222-224)
- `_estimate_hybrid()` (line 263-284)
- `_estimate_pointmap()` (line 286-322)
- `estimate_pose()` (line 226-261) — replace with `estimate_poses()`

**Add new:**

```python
import torch
from PIL import Image
from scipy.spatial.transform import Rotation as R

# SAM 3 imports
sys.path.insert(0, os.path.join(_this_dir, "sam3"))
from sam3 import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor


def pca_rotation_with_gravity(points_3d: np.ndarray) -> np.ndarray:
    """Compute rotation matrix from PCA on 3D points with gravity correction.

    1. PCA → 3 eigenvectors sorted by eigenvalue (descending)
    2. PC1 = longest axis, PC2 = second axis, PC3 = shortest (normal)
    3. Gravity correction: ensure PC3 (normal) aligns with -Y (up in camera frame)
       since objects sit on a table with gravity pointing +Y (down)
    4. Enforce right-hand rule: det(R) = 1

    Args:
        points_3d: (N, 3) array of 3D points in camera frame.

    Returns:
        (3, 3) rotation matrix (orthonormal, det=1) in camera frame.
    """
    centered = points_3d - points_3d.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # eigh returns ascending order; reverse to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx]

    # Gravity correction: PC3 (shortest axis / surface normal) should point
    # roughly upward (-Y in camera frame) for tabletop objects
    gravity_dir = np.array([0.0, -1.0, 0.0])  # up in camera frame
    if np.dot(eigenvectors[:, 2], gravity_dir) < 0:
        eigenvectors[:, 2] *= -1

    # Ensure right-hand rule
    if np.linalg.det(eigenvectors) < 0:
        eigenvectors[:, 1] *= -1

    return eigenvectors  # columns are the axes


def rotation_matrix_to_rpy(R_mat: np.ndarray) -> Tuple[float, float, float]:
    """Convert 3x3 rotation matrix to roll, pitch, yaw in degrees."""
    rpy = R.from_matrix(R_mat).as_euler('xyz', degrees=True)
    return float(rpy[0]), float(rpy[1]), float(rpy[2])


class PoseEstimator:
    """6DoF pose estimation using SAM 3 segmentation + depth PCA.

    Args:
        device: torch device ("cuda" or "cpu").
        confidence_threshold: SAM 3 mask confidence threshold.
    """

    def __init__(self, device: str = "cuda", confidence_threshold: float = 0.5):
        model = build_sam3_image_model(device=device, eval_mode=True)
        self._processor = Sam3Processor(model, device=device,
                                         confidence_threshold=confidence_threshold)
        self._device = device

    def estimate_poses(
        self,
        rgb_or_bgr: np.ndarray,
        depth_mm: np.ndarray,
        intrinsics: Tuple[float, float, float, float],
        prompt: str = "object",
        is_bgr: bool = True,
    ) -> list:
        """Estimate 6DoF poses for all objects matching the text prompt.

        Args:
            rgb_or_bgr: (H, W, 3) uint8 color image.
            depth_mm: (H, W) uint16 depth in millimeters.
            intrinsics: (fx, fy, cx, cy) camera intrinsics.
            prompt: Text prompt for SAM 3 segmentation (e.g., "object", "cup", "box").
            is_bgr: If True, convert BGR→RGB before SAM 3.

        Returns:
            List[ObjectPose] for each detected object.
        """
        # Convert BGR → RGB if needed
        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr

        # SAM 3 segmentation
        pil_image = Image.fromarray(rgb)
        state = self._processor.set_image(pil_image)
        state = self._processor.set_text_prompt(prompt=prompt, state=state)

        masks = state["masks"]   # (N, H, W) tensor
        scores = state["scores"]  # (N,) tensor

        if masks is None or len(masks) == 0:
            return []

        # Convert masks to numpy
        masks_np = masks.cpu().numpy().astype(bool)

        fx, fy, cx, cy = intrinsics
        poses = []

        for i in range(len(masks_np)):
            mask = masks_np[i]

            if not mask.any():
                continue

            # Deproject to 3D
            points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)

            if len(points) < 3:
                continue  # Need at least 3 points for PCA

            # Translation: centroid
            x, y, z = compute_centroid(points)

            # Orientation: PCA + gravity
            R_mat = pca_rotation_with_gravity(points)
            roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

            poses.append(ObjectPose(
                x=x, y=y, z=z,
                roll=roll, pitch=pitch, yaw=yaw,
                method="sam3_pca"
            ))

        return poses
```

### Step 3: Update `__main__` block
- Remove SAM 3D Objects config argument
- Add `--prompt` argument (default: "object")
- Remove `--method` argument (only one method now)
- Call `estimate_poses()` and print all results
- Keep `--fx/--fy/--cx/--cy` and auto-detect intrinsics

### Step 4: Verification
- Run with RealSense capture and verify masks are generated
- Verify poses have reasonable values (z > 0, RPY in expected ranges)
- Verify `det(R) = 1` for all rotation matrices
- Test with `from pose_estimator import PoseEstimator, ObjectPose`

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SAM 3 model not downloaded / HF auth needed | Blocks all inference | Document HF auth requirement; add clear error message in `__init__` |
| PCA sign ambiguity not fully resolved by gravity | Inconsistent orientation across frames | Gravity correction handles 180° flip on normal axis; remaining 180° ambiguity on table plane is inherent to PCA and acceptable for pick-and-place |
| SAM 3 text prompt "object" too generic | Poor segmentation quality | Make prompt configurable; user can specify "cup", "box", etc. |
| SAM 3 masks don't align with depth resolution | Misaligned pose | SAM 3 resizes to 1008x1008 internally but returns masks at original resolution; verify alignment |
| Too few depth points in mask (thin objects) | PCA fails | Skip objects with < 3 valid depth points; log warning |

## Verification Steps
1. `python -c "from pose_estimator import PoseEstimator, ObjectPose"` succeeds
2. `grep -r "sam-3d-objects\|sam_3d_objects\|from inference import" pose_estimator.py` returns nothing
3. `python pose_estimator.py --prompt "object"` with RealSense connected prints detected poses
4. Each pose has z > 0 (object in front of camera)
5. PCA rotation matrices all have det ≈ 1.0
