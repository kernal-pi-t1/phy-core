# Plan: SAM 3 Mask + RealSense Depth PCA 6DoF Pose Estimation (v2)

## Source Spec
- `/home/robot/jm_ws/.omc/specs/deep-interview-sam3-pca-pose.md`

## Requirements Summary
Replace existing `pose_estimator.py` (SAM 3D Objects) with a new pipeline:
1. SAM 3 text-prompt segmentation → N object masks
2. Per-mask: RealSense depth deprojection → 3D point cloud
3. PCA on point cloud → rotation matrix + gravity correction (Y-down)
4. Centroid → translation (x, y, z meters)
5. Output: `List[ObjectPose]` with 6DoF per object

**Spec deviation note**: The deep-interview spec says "auto segmentation" but SAM 3's API only supports text-prompt segmentation (`Sam3Processor.set_text_prompt()`). There is no auto-mask-generator. The plan adapts by making the text prompt configurable (default: `"object"`).

## RALPLAN-DR Summary

### Principles
1. **Simplicity over generality**: PCA + gravity is intentionally simple; avoid over-engineering rotation estimation
2. **Reuse existing utilities**: Keep `deproject_depth_to_points()`, `compute_centroid()`, `validate_inputs()`, `ObjectPose` dataclass
3. **Clean dependency cut**: Fully remove SAM 3D Objects imports; no backward compatibility shims
4. **Text-prompt segmentation**: SAM 3 requires text prompts; design the API around configurable text prompts
5. **Deterministic orientation**: PCA eigenvectors have sign ambiguity; gravity correction resolves this for tabletop pick-and-place

### Decision Drivers
1. **SAM 3 API constraint**: SAM 3 uses `set_text_prompt(prompt)` — module must accept text prompts
2. **PCA sign ambiguity**: Gravity vector (Y-down) provides consistent reference to resolve 180° flip
3. **Multi-object output**: New pipeline returns `List[ObjectPose]` for all segmented objects
4. **External mask support**: Existing callers use `--mask` to provide pre-computed masks; this capability must be preserved (Architect synthesis)

### Viable Options

#### Option A: Monolithic with escape hatch (Selected — Architect synthesis)
- Single class wraps SAM 3 model loading + PCA pose estimation
- High-level: `estimate_poses(rgb, depth, intrinsics, prompt)` → `List[ObjectPose]` (SAM 3 + PCA)
- Low-level: `estimate_pose_from_mask(depth, mask, intrinsics)` → `ObjectPose` (PCA only, external mask)
- **Pros**: Simple primary API, model loaded once, external mask escape hatch preserved
- **Cons**: Single file, slightly larger class surface

#### Option B: Separate Segmentor + PoseEstimator
- Two classes: `Sam3Segmentor` + `PcaPoseEstimator`
- **Invalidation**: Extra abstraction without current benefit; user chose full replacement, not pluggable system. The escape hatch in Option A provides sufficient flexibility for external masks.

## Acceptance Criteria
- [ ] `pose_estimator.py` fully replaced with SAM 3 + PCA implementation
- [ ] No imports from `sam-3d-objects/` remain
- [ ] `from pose_estimator import PoseEstimator, ObjectPose` works
- [ ] `PoseEstimator(device="cuda")` loads SAM 3 model
- [ ] `estimate_poses(rgb_bgr, depth_mm, intrinsics, prompt="object")` returns `List[ObjectPose]`
- [ ] `estimate_pose_from_mask(depth_mm, mask, intrinsics)` returns single `ObjectPose` (external mask support)
- [ ] Each `ObjectPose` has x,y,z (meters), roll,pitch,yaw (degrees) in OpenCV camera frame
- [ ] PCA rotation matrix has det(R)=1 (right-hand rule enforced)
- [ ] Gravity correction aligns Y-axis with camera Y-down
- [ ] Degenerate point clouds (collinear/planar) handled gracefully with warning
- [ ] SAM 3 mask shape `(N, 1, H, W)` correctly squeezed to `(N, H, W)`
- [ ] Input validation (depth dtype, spatial dims) applied before processing
- [ ] `__main__` block supports both `--prompt` (SAM 3) and `--mask` (external mask) modes
- [ ] Works with 640x480 RealSense input (uint16 depth, BGR color)

## Implementation Steps

### Step 1: Understand SAM 3 API (no code changes)
- Verify `Sam3Processor` from `sam3/sam3/model/sam3_image_processor.py`
- Confirm mask output shape is `(N, 1, H, W)` (line 211-219)
- Confirm `build_sam3_image_model()` from `sam3/sam3/model_builder.py`

### Step 2: Rewrite `pose_estimator.py`

**Keep unchanged:**
- `ObjectPose` dataclass (line 38-47)
- `deproject_depth_to_points()` (line 75-104)
- `compute_centroid()` (line 107-119)

**Modify:**
- `validate_inputs()` (line 54-72): Make mask parameter optional; when mask is None, only validate rgb and depth shapes/dtypes

**Remove entirely:**
- Lines 28-31: `sam-3d-objects` path setup
- `quaternion_pytorch3d_to_rpy_camera()` (line 122-156)
- `depth_to_pointmap()` (line 159-186)
- `pointmap_camera_to_pytorch3d()` (line 189-208)
- Old `PoseEstimator` class (line 211-322)

**Add new functions:**

```python
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# SAM 3 imports
sys.path.insert(0, os.path.join(_this_dir, "sam3"))
from sam3 import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor


def pca_rotation_with_gravity(points_3d: np.ndarray) -> np.ndarray:
    """Compute rotation matrix from PCA on 3D points with gravity correction.

    Steps:
    1. PCA → 3 eigenvectors sorted by eigenvalue (descending)
    2. PC1 = longest axis, PC2 = second, PC3 = shortest (surface normal)
    3. Gravity correction: PC3 aligns with -Y (up in OpenCV camera frame)
    4. Enforce right-hand rule: det(R) = 1

    Returns (3, 3) rotation matrix. Returns identity with warning for
    degenerate point clouds (collinear or insufficient spread).
    """
    centered = points_3d - points_3d.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # eigh returns ascending; reverse to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Degenerate guard: if smallest eigenvalue is near-zero relative to largest,
    # the point cloud is nearly planar or collinear — PCA axes are unreliable
    if eigenvalues[0] > 0 and eigenvalues[2] / eigenvalues[0] < 1e-6:
        logger.warning(
            "Degenerate point cloud (eigenvalue ratio %.2e). "
            "Returning identity rotation.", eigenvalues[2] / eigenvalues[0]
        )
        return np.eye(3)

    # Gravity correction: PC3 (normal) should point roughly upward (-Y in camera)
    gravity_up = np.array([0.0, -1.0, 0.0])
    if np.dot(eigenvectors[:, 2], gravity_up) < 0:
        eigenvectors[:, 2] *= -1

    # Enforce right-hand rule
    if np.linalg.det(eigenvectors) < 0:
        eigenvectors[:, 1] *= -1

    return eigenvectors


def rotation_matrix_to_rpy(R_mat: np.ndarray) -> Tuple[float, float, float]:
    """Convert 3x3 rotation matrix to roll, pitch, yaw in degrees."""
    rpy = R.from_matrix(R_mat).as_euler('xyz', degrees=True)
    return float(rpy[0]), float(rpy[1]), float(rpy[2])
```

**Add new PoseEstimator class:**

```python
class PoseEstimator:
    """6DoF pose estimation using SAM 3 segmentation + depth PCA.

    Two usage modes:
    1. estimate_poses(): SAM 3 text-prompt segmentation → N masks → N poses
    2. estimate_pose_from_mask(): External mask → single pose (no SAM 3)
    """

    def __init__(self, device: str = "cuda", confidence_threshold: float = 0.5):
        model = build_sam3_image_model(device=device, eval_mode=True)
        self._processor = Sam3Processor(
            model, device=device, confidence_threshold=confidence_threshold
        )
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

        Returns List[ObjectPose]. Empty list if no objects detected.
        """
        validate_inputs(rgb_or_bgr, depth_mm)  # No mask — SAM 3 generates them

        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr
        pil_image = Image.fromarray(rgb)

        state = self._processor.set_image(pil_image)
        state = self._processor.set_text_prompt(prompt=prompt, state=state)

        masks = state["masks"]  # (N, 1, H, W)
        scores = state["scores"]

        if masks is None or len(masks) == 0:
            logger.warning("SAM 3 detected no objects for prompt '%s'", prompt)
            return []

        masks_np = masks.squeeze(1).cpu().numpy().astype(bool)  # (N, H, W)
        fx, fy, cx, cy = intrinsics
        poses = []

        for i in range(len(masks_np)):
            mask = masks_np[i]
            if not mask.any():
                logger.warning("Mask %d is empty, skipping", i)
                continue

            points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)
            if len(points) < 3:
                logger.warning("Mask %d has only %d valid depth points, skipping", i, len(points))
                continue

            x, y, z = compute_centroid(points)
            R_mat = pca_rotation_with_gravity(points)
            roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

            poses.append(ObjectPose(
                x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="sam3_pca"
            ))

        logger.info("Detected %d objects, estimated %d poses", len(masks_np), len(poses))
        return poses

    def estimate_pose_from_mask(
        self,
        depth_mm: np.ndarray,
        mask: np.ndarray,
        intrinsics: Tuple[float, float, float, float],
    ) -> ObjectPose:
        """Estimate 6DoF pose from a pre-computed mask (no SAM 3 needed).

        Args:
            depth_mm: (H, W) uint16 depth in mm.
            mask: (H, W) binary mask.
            intrinsics: (fx, fy, cx, cy).

        Returns:
            ObjectPose with method="pca".
        """
        if mask.ndim == 3 and mask.shape[2] == 1:
            mask = mask[:, :, 0]
        if mask.ndim != 2:
            raise ValueError(f"Mask must be 2D, got shape {mask.shape}")
        if depth_mm.dtype != np.uint16:
            raise ValueError(f"Depth must be uint16, got {depth_mm.dtype}")
        if mask.shape != depth_mm.shape:
            raise ValueError(f"Mask {mask.shape} != depth {depth_mm.shape}")
        if not mask.any():
            raise ValueError("Mask is empty")

        fx, fy, cx, cy = intrinsics
        points = deproject_depth_to_points(depth_mm, mask, fx, fy, cx, cy)
        if len(points) < 3:
            raise ValueError(f"Only {len(points)} valid depth points, need at least 3")

        x, y, z = compute_centroid(points)
        R_mat = pca_rotation_with_gravity(points)
        roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

        return ObjectPose(x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="pca")
```

### Step 3: Update `__main__` block

```python
if __name__ == "__main__":
    import argparse
    import cv2

    parser = argparse.ArgumentParser(description="6DoF pose estimation with SAM 3 + PCA")
    parser.add_argument("--prompt", default="object", help="SAM 3 text prompt")
    parser.add_argument("--mask", default=None, help="Path to external mask (skip SAM 3)")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--confidence", type=float, default=0.5)
    parser.add_argument("--fx", type=float, default=None)
    parser.add_argument("--fy", type=float, default=None)
    parser.add_argument("--cx", type=float, default=None)
    parser.add_argument("--cy", type=float, default=None)
    args = parser.parse_args()

    from capture_realsense import capture_single_frame
    depth_mm, color_bgr = capture_single_frame()

    # Intrinsics (auto-detect or manual)
    # ... (keep existing auto-detect logic)

    estimator = PoseEstimator(device=args.device, confidence_threshold=args.confidence)

    if args.mask:
        # External mask mode
        mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE) > 0
        pose = estimator.estimate_pose_from_mask(depth_mm, mask, intrinsics)
        print(f"[PCA] x={pose.x:.4f}m y={pose.y:.4f}m z={pose.z:.4f}m "
              f"roll={pose.roll:.2f}° pitch={pose.pitch:.2f}° yaw={pose.yaw:.2f}°")
    else:
        # SAM 3 text-prompt mode
        poses = estimator.estimate_poses(color_bgr, depth_mm, intrinsics, prompt=args.prompt)
        for i, pose in enumerate(poses):
            print(f"[Object {i}] x={pose.x:.4f}m y={pose.y:.4f}m z={pose.z:.4f}m "
                  f"roll={pose.roll:.2f}° pitch={pose.pitch:.2f}° yaw={pose.yaw:.2f}°")
```

### Step 4: Verification
1. `python -c "from pose_estimator import PoseEstimator, ObjectPose"` succeeds
2. `grep -r "sam-3d-objects\|from inference import" pose_estimator.py` returns nothing
3. `python pose_estimator.py --prompt "object"` prints detected poses
4. `python pose_estimator.py --mask mask.png` works with external mask
5. Each pose has z > 0
6. PCA rotation matrices have det ≈ 1.0

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SAM 3 HF auth / model not downloaded | Blocks inference | Clear error message in `__init__`; document `hf auth login` requirement |
| PCA 180° in-plane ambiguity | Inconsistent yaw between frames | Inherent to PCA; gravity corrects normal axis; acceptable for top-down pick |
| SAM 3 "object" prompt too generic | Poor/noisy segmentation | Configurable prompt; user specifies object class |
| Mask shape mismatch (N,1,H,W) | Wrong pose | `.squeeze(1)` applied; validated by Architect |
| Degenerate point cloud | Meaningless rotation | Eigenvalue ratio guard → identity rotation + warning |
| CUDA OOM on large images | Crash | SAM 3 resizes to 1008x1008 internally; 640x480 input is well within limits |

## Verification Steps
1. `python -c "from pose_estimator import PoseEstimator, ObjectPose"` succeeds
2. `grep -r "sam-3d-objects\|sam_3d_objects\|from inference import" pose_estimator.py` returns nothing
3. `python pose_estimator.py --prompt "object"` with RealSense prints poses
4. `python pose_estimator.py --mask <path>` with external mask prints single pose
5. All z values > 0 (object in front of camera)
6. All rotation matrices have det ≈ 1.0 (verified in unit test)
7. No `sam-3d-objects` references in any import

## Breaking Changes
- `PoseEstimator(config_path)` → `PoseEstimator(device="cuda")`
- `estimate_pose(rgb, depth, mask, intrinsics)` → `estimate_poses(rgb, depth, intrinsics, prompt)` returns `List[ObjectPose]`
- For external masks: use `estimate_pose_from_mask(depth, mask, intrinsics)` instead
- `ObjectPose.method` values: `"hybrid"/"pointmap"` → `"sam3_pca"/"pca"`
- New dependency: `Pillow` (PIL)

## Changelog (v2 from Architect review)
- Fixed: Mask shape handling — `.squeeze(1)` for `(N, 1, H, W)` → `(N, H, W)`
- Added: `estimate_pose_from_mask()` for external mask support (Architect synthesis)
- Added: Input validation in `estimate_poses()` via modified `validate_inputs()`
- Added: `logging.warning()` for all skip conditions (empty mask, few points, no detections)
- Added: Degenerate point cloud guard (eigenvalue ratio check) in `pca_rotation_with_gravity()`
- Added: Breaking changes documentation
- Added: Spec deviation note (auto-seg → text-prompt)
