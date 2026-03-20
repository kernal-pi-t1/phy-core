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

**Spec deviation note**: The deep-interview spec says "auto segmentation" but SAM 3's API only supports text-prompt segmentation (`Sam3Processor.set_text_prompt()`). There is no auto-mask-generator. The plan adapts by making the text prompt configurable (default: `"object"`).

## RALPLAN-DR Summary

### Principles
1. **Simplicity over generality**: PCA + gravity is intentionally simple; avoid over-engineering rotation estimation
2. **Reuse existing utilities**: Keep `deproject_depth_to_points()`, `compute_centroid()`, `ObjectPose` dataclass
3. **Clean dependency cut**: Fully remove SAM 3D Objects imports; no backward compatibility shims
4. **Text-prompt segmentation**: SAM 3 requires text prompts; design the API around configurable text prompts
5. **Deterministic orientation**: PCA eigenvectors have sign ambiguity; gravity correction resolves this for tabletop pick-and-place

### Decision Drivers
1. **SAM 3 API constraint**: SAM 3 uses `set_text_prompt(prompt)` — module must accept text prompts
2. **PCA sign ambiguity**: Gravity vector (Y-down) provides consistent reference to resolve 180° flip
3. **Multi-object output**: New pipeline returns `List[ObjectPose]` for all segmented objects
4. **External mask support**: Existing `__main__` block uses `--mask` for pre-computed masks; this capability must be preserved

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

## ADR (Architecture Decision Record)

### Decision
Use a monolithic `PoseEstimator` class with two public methods: `estimate_poses()` (SAM 3 + PCA) and `estimate_pose_from_mask()` (PCA only).

### Drivers
- SAM 3 requires text-prompt input (no auto-mask-generator)
- Existing callers use external masks via `--mask` CLI argument
- Simplicity principle: single class, single file, single import

### Alternatives Considered
- **Option B (Separate classes)**: Rejected because the escape hatch method in Option A provides equivalent flexibility with less API surface. No current callers need to swap segmentation backends.

### Why Chosen
Option A preserves the single-file, single-class pattern of the existing `pose_estimator.py` while adding external mask support. The PCA pose logic is simple enough that separating it into its own class adds complexity without testability benefit (the pure functions `pca_rotation_with_gravity()` and `rotation_matrix_to_rpy()` are already independently testable).

### Consequences
- Breaking API change: `estimate_pose()` → `estimate_poses()` (returns list), `estimate_pose_from_mask()` for single masks
- SAM 3 model always loaded in constructor, even for mask-only usage (acceptable for current use case)
- Future segmentation backend swaps require modifying PoseEstimator class internally

### Follow-ups
- If multiple segmentation backends are needed later, refactor to Option B
- Consider lazy SAM 3 loading if mask-only usage becomes common

## Acceptance Criteria
- [ ] `pose_estimator.py` fully replaced with SAM 3 + PCA implementation
- [ ] No imports from `sam-3d-objects/` remain
- [ ] `from pose_estimator import PoseEstimator, ObjectPose` works
- [ ] `PoseEstimator(device="cuda")` loads SAM 3 model
- [ ] `estimate_poses(rgb_bgr, depth_mm, intrinsics, prompt="object")` returns `List[ObjectPose]`
- [ ] `estimate_pose_from_mask(depth_mm, mask, intrinsics)` returns single `ObjectPose` (external mask support)
- [ ] Each `ObjectPose` has x,y,z (meters), roll,pitch,yaw (degrees) in OpenCV camera frame
- [ ] PCA rotation matrix has det(R)=1 (right-hand rule enforced)
- [ ] Gravity correction aligns PC3 with -Y (up in camera frame)
- [ ] Degenerate point clouds (all-zero eigenvalues, collinear, planar) handled gracefully with warning + identity rotation
- [ ] SAM 3 mask shape `(N, 1, H, W)` correctly squeezed to `(N, H, W)`
- [ ] Input validation: depth dtype uint16, rgb/depth spatial dims match
- [ ] `__main__` block supports both `--prompt` (SAM 3) and `--mask` (external mask) modes
- [ ] Works with 640x480 RealSense input (uint16 depth, BGR color)

## Implementation Steps

### Step 1: Verify SAM 3 API (no code changes)
- Verify `Sam3Processor` from `sam3/sam3/model/sam3_image_processor.py`
- Confirm mask output shape is `(N, 1, H, W)` (line 211-219 of that file)
- Confirm `build_sam3_image_model()` from `sam3/sam3/model_builder.py`

### Step 2: Rewrite `pose_estimator.py`

**Keep unchanged:**
- `ObjectPose` dataclass (`pose_estimator.py:38-47`)
- `deproject_depth_to_points()` (`pose_estimator.py:75-104`)
- `compute_centroid()` (`pose_estimator.py:107-119`)

**Modify `validate_inputs()`** (`pose_estimator.py:54-72`):
```python
def validate_inputs(
    rgb: np.ndarray,
    depth_mm: np.ndarray,
    mask: np.ndarray | None = None,
) -> np.ndarray | None:
    """Validate inputs. Returns the (possibly squeezed) mask, or None if not provided."""
    if depth_mm.dtype != np.uint16:
        raise ValueError(f"Depth must be uint16 (mm), got {depth_mm.dtype}")
    if rgb.shape[:2] != depth_mm.shape[:2]:
        raise ValueError(
            f"RGB spatial dims {rgb.shape[:2]} != depth dims {depth_mm.shape[:2]}"
        )
    if mask is None:
        return None
    if mask.ndim == 3 and mask.shape[2] == 1:
        mask = mask[:, :, 0]
    if mask.ndim != 2:
        raise ValueError(f"Mask must be 2D (H,W), got shape {mask.shape}")
    if mask.shape != depth_mm.shape:
        raise ValueError(f"Mask shape {mask.shape} != depth shape {depth_mm.shape}")
    if not mask.any():
        raise ValueError("Mask is entirely empty (no True pixels)")
    return mask
```

**Remove entirely:**
- Lines 19-20, 28-31: `sys.path.insert` for `sam-3d-objects`
- `quaternion_pytorch3d_to_rpy_camera()` (`pose_estimator.py:122-156`)
- `depth_to_pointmap()` (`pose_estimator.py:159-186`)
- `pointmap_camera_to_pytorch3d()` (`pose_estimator.py:189-208`)
- Old `PoseEstimator` class (`pose_estimator.py:211-322`)
- Old `__main__` block (`pose_estimator.py:325-404`)

**Add new imports (top of file):**
```python
import logging
from typing import List, Optional
from PIL import Image

logger = logging.getLogger(__name__)

# SAM 3 imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_this_dir, "sam3"))
from sam3 import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor
```

**Add new pure functions:**
```python
def pca_rotation_with_gravity(points_3d: np.ndarray) -> np.ndarray:
    """Compute rotation matrix from PCA on 3D points with gravity correction.

    Steps:
    1. PCA → 3 eigenvectors sorted by eigenvalue (descending)
    2. PC1 = longest axis, PC2 = second, PC3 = shortest (surface normal)
    3. Gravity correction: PC3 aligns with -Y (up in OpenCV camera frame)
    4. Enforce right-hand rule: det(R) = 1

    Returns (3, 3) rotation matrix. Returns identity with warning for
    degenerate point clouds.
    """
    centered = points_3d - points_3d.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # eigh returns ascending; reverse to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Degenerate guard: all-zero or near-singular covariance
    if eigenvalues[0] <= 0:
        logger.warning("All eigenvalues <= 0 (identical points). Returning identity rotation.")
        return np.eye(3)

    if eigenvalues[2] / eigenvalues[0] < 1e-6:
        logger.warning(
            "Degenerate point cloud (eigenvalue ratio %.2e). "
            "Returning identity rotation.", eigenvalues[2] / eigenvalues[0]
        )
        return np.eye(3)

    # Gravity correction: PC3 (normal) should point roughly upward (-Y in camera frame)
    gravity_up = np.array([0.0, -1.0, 0.0])
    if np.dot(eigenvectors[:, 2], gravity_up) < 0:
        eigenvectors[:, 2] *= -1

    # Enforce right-hand rule: det(R) must be +1
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
    ) -> List[ObjectPose]:
        """Estimate 6DoF poses for all objects matching the text prompt.

        Args:
            rgb_or_bgr: (H, W, 3) uint8 color image.
            depth_mm: (H, W) uint16 depth in millimeters.
            intrinsics: (fx, fy, cx, cy) camera intrinsics.
            prompt: Text prompt for SAM 3 (e.g., "object", "cup", "box").
            is_bgr: If True, convert BGR→RGB before SAM 3.

        Returns:
            List[ObjectPose] for each detected object. Empty list if none found.
        """
        validate_inputs(rgb_or_bgr, depth_mm)

        rgb = rgb_or_bgr[..., ::-1].copy() if is_bgr else rgb_or_bgr
        pil_image = Image.fromarray(rgb)

        state = self._processor.set_image(pil_image)
        state = self._processor.set_text_prompt(prompt=prompt, state=state)

        masks = state["masks"]  # (N, 1, H, W) from sam3_image_processor.py:219

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
                logger.warning(
                    "Mask %d has only %d valid depth points, skipping", i, len(points)
                )
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
            mask: (H, W) binary mask for target object.
            intrinsics: (fx, fy, cx, cy).

        Returns:
            ObjectPose with method="pca".

        Raises:
            ValueError: If inputs are invalid or insufficient depth points.
        """
        # Validate mask
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
            raise ValueError(f"Only {len(points)} valid depth points, need >= 3")

        x, y, z = compute_centroid(points)
        R_mat = pca_rotation_with_gravity(points)
        roll, pitch, yaw = rotation_matrix_to_rpy(R_mat)

        return ObjectPose(x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, method="pca")
```

### Step 3: Update `__main__` block

Replace existing `__main__` block (`pose_estimator.py:325-404`) with:

```python
if __name__ == "__main__":
    import argparse
    import cv2

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="6DoF pose estimation with SAM 3 + PCA")
    parser.add_argument("--prompt", default="object", help="SAM 3 text prompt (default: object)")
    parser.add_argument("--mask", default=None, help="Path to external mask PNG (skips SAM 3)")
    parser.add_argument("--device", default="cuda", help="torch device")
    parser.add_argument("--confidence", type=float, default=0.5, help="SAM 3 confidence threshold")
    parser.add_argument("--fx", type=float, default=None)
    parser.add_argument("--fy", type=float, default=None)
    parser.add_argument("--cx", type=float, default=None)
    parser.add_argument("--cy", type=float, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # --- Capture from RealSense ---
    from capture_realsense import capture_single_frame
    depth_mm, color_bgr = capture_single_frame()
    print(f"Captured: color {color_bgr.shape}, depth {depth_mm.shape}")

    # --- Intrinsics (from args or auto-detect) ---
    if all(v is not None for v in [args.fx, args.fy, args.cx, args.cy]):
        intrinsics = (args.fx, args.fy, args.cx, args.cy)
    else:
        import pyrealsense2 as rs
        print("Auto-detecting intrinsics (provide --fx/--fy/--cx/--cy to skip)...")
        try:
            pipe = rs.pipeline()
            cfg = rs.config()
            cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            profile = pipe.start(cfg)
            intr = profile.get_stream(
                rs.stream.color
            ).as_video_stream_profile().get_intrinsics()
            pipe.stop()
            intrinsics = (intr.fx, intr.fy, intr.ppx, intr.ppy)
            print(f"Auto-detected intrinsics: fx={intr.fx:.1f}, fy={intr.fy:.1f}, "
                  f"cx={intr.ppx:.1f}, cy={intr.ppy:.1f}")
        except RuntimeError as e:
            print(f"ERROR: Failed to auto-detect intrinsics: {e}", file=sys.stderr)
            print("Please provide --fx, --fy, --cx, --cy manually.", file=sys.stderr)
            sys.exit(1)

    # --- Estimate pose ---
    estimator = PoseEstimator(device=args.device, confidence_threshold=args.confidence)

    if args.mask:
        # External mask mode (no SAM 3 segmentation)
        mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE) > 0
        print(f"Mask: {mask.shape}, {mask.sum()} pixels selected")
        pose = estimator.estimate_pose_from_mask(depth_mm, mask, intrinsics)
        print(f"\n[PCA]  x={pose.x:.4f}m  y={pose.y:.4f}m  z={pose.z:.4f}m  "
              f"roll={pose.roll:.2f}\u00b0  pitch={pose.pitch:.2f}\u00b0  yaw={pose.yaw:.2f}\u00b0")
    else:
        # SAM 3 text-prompt segmentation mode
        print(f"Running SAM 3 segmentation with prompt: '{args.prompt}'")
        poses = estimator.estimate_poses(
            color_bgr, depth_mm, intrinsics, prompt=args.prompt
        )
        if not poses:
            print("No objects detected.")
        for i, pose in enumerate(poses):
            print(f"[Object {i}]  x={pose.x:.4f}m  y={pose.y:.4f}m  z={pose.z:.4f}m  "
                  f"roll={pose.roll:.2f}\u00b0  pitch={pose.pitch:.2f}\u00b0  yaw={pose.yaw:.2f}\u00b0")
```

### Step 4: Verification
1. `python -c "from pose_estimator import PoseEstimator, ObjectPose"` succeeds
2. `grep -r "sam-3d-objects\|sam_3d_objects\|from inference import" pose_estimator.py` returns nothing
3. `python pose_estimator.py --prompt "object"` with RealSense prints detected poses
4. `python pose_estimator.py --mask <path>` with external mask prints single pose
5. Each pose has z > 0 (object in front of camera)
6. All rotation matrices have det ≈ 1.0
7. No `sam-3d-objects` references in any import

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SAM 3 HF auth / model not downloaded | Blocks all inference | Clear error from HF hub; document `hf auth login` requirement |
| PCA 180° in-plane ambiguity | Inconsistent yaw between frames | Inherent to PCA; gravity corrects normal axis; acceptable for top-down pick |
| SAM 3 "object" prompt too generic | Poor/noisy segmentation | Configurable prompt; user specifies object class (e.g., "cup", "box") |
| Mask shape `(N,1,H,W)` vs `(N,H,W)` | Wrong pose computation | `.squeeze(1)` applied; confirmed by reading `sam3_image_processor.py:211-219` |
| Degenerate point cloud (collinear/identical) | Meaningless rotation | Eigenvalue ratio + zero guard → identity rotation + warning |
| CUDA OOM | Crash | SAM 3 resizes to 1008x1008 internally; 640x480 input well within limits |

## Breaking Changes
- `PoseEstimator(config_path)` → `PoseEstimator(device="cuda")`
- `estimate_pose(rgb, depth, mask, intrinsics)` → `estimate_poses(rgb, depth, intrinsics, prompt)` returns `List[ObjectPose]`
- For external masks: use `estimate_pose_from_mask(depth, mask, intrinsics)` instead
- `ObjectPose.method` values: `"hybrid"/"pointmap"` → `"sam3_pca"/"pca"`
- New dependency: `Pillow` (PIL)
- Removed dependency: `sam-3d-objects` (entire submodule)

## Consensus Changelog
- **v1 → v2 (Architect)**: Fixed mask shape `.squeeze(1)`; added `estimate_pose_from_mask()`; added input validation; added logging; added degenerate guard; documented breaking changes
- **v2 → final (Critic)**: Added `eigenvalues[0] <= 0` guard; specified `validate_inputs()` new signature; completed `__main__` intrinsics block; fixed return type annotation to `List[ObjectPose]`; added ADR section
