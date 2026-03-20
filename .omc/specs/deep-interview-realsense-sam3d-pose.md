# Deep Interview Spec: RealSense + SAM 3D Object 6DoF Pose Estimation Pipeline

## Metadata
- Interview ID: rs-sam3d-pose-001
- Rounds: 6
- Final Ambiguity Score: 15.2%
- Type: brownfield
- Generated: 2026-03-21
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.95 | 0.35 | 0.333 |
| Constraint Clarity | 0.80 | 0.25 | 0.200 |
| Success Criteria | 0.75 | 0.25 | 0.188 |
| Context Clarity | 0.85 | 0.15 | 0.128 |
| **Total Clarity** | | | **0.848** |
| **Ambiguity** | | | **15.2%** |

## Goal
Build an importable Python module that takes a RealSense RGB image, depth image, and a pre-generated segmentation mask as input, runs SAM 3D Objects inference to estimate each segmented object's 6DoF pose (x, y, z, roll, pitch, yaw) in the camera coordinate frame, and returns the result as a Python dict/dataclass. The module provides **two pose estimation strategies** for comparison:

1. **Method A (Hybrid):** SAM 3D (MoGe-based) for rotation (r, p, y) + RealSense metric depth for translation (x, y, z) via masked 3D centroid
2. **Method B (Pointmap injection):** RealSense depth converted to pointmap and directly injected into SAM 3D's `compute_pointmap(pointmap=...)` for full pose

## Constraints
- Input: RGB image (numpy array, BGR or RGB), depth image (numpy uint16, mm units), binary segmentation mask (numpy bool/uint8), RealSense camera intrinsics
- Output: Python dataclass with `x, y, z` (meters), `roll, pitch, yaw` (degrees), camera coordinate frame
- Camera input via `capture_realsense.capture_single_frame()` (existing module)
- SAM 3D inference via existing `Inference` class from `sam-3d-objects/notebook/inference.py`
- Must handle PyTorch3D coordinate convention (SAM 3D output) and convert to standard camera frame
- Quaternion (w,x,y,z) from `pose_decoder` → RPY conversion using scipy
- RealSense depth is metric (mm) → convert to meters for output
- Module must be importable (class/function), not just a script
- GPU required (SAM 3D uses CUDA)

## Non-Goals
- Segmentation mask generation (masks are pre-generated, provided as input)
- ROS integration (output is Python dict/dataclass, not ROS messages)
- Multi-object scene composition / Gaussian Splat merging
- Real-time performance optimization
- Model training or fine-tuning

## Acceptance Criteria
- [ ] Module is importable: `from pose_estimator import PoseEstimator` or similar
- [ ] Accepts RGB image, depth image, mask, and intrinsics as inputs
- [ ] Method A: Returns x,y,z (meters) from RealSense depth centroid + r,p,y (degrees) from SAM 3D
- [ ] Method B: Returns x,y,z,r,p,y from SAM 3D with RealSense pointmap injection
- [ ] Output is a dataclass/dict with fields: x, y, z (float, meters), roll, pitch, yaw (float, degrees)
- [ ] Coordinate frame is camera frame (z forward, x right, y down — standard camera convention)
- [ ] Works with capture_realsense.py's output (640x480, uint16 depth, BGR color)
- [ ] Both methods can be selected via a parameter (e.g., `method="hybrid"` or `method="pointmap"`)
- [ ] Includes a `__main__` block for standalone testing with RealSense capture

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| RealSense depth should replace MoGe | Contrarian: MoGe is what the model was trained on | Implement both methods for comparison |
| Hybrid is always better | Contrarian: Direct pointmap injection may work | Both methods implemented, user decides |
| Output needs ROS format | Asked about use case | Python dict/dataclass sufficient for now |
| Mask generation is part of pipeline | Asked about mask source | Masks are pre-generated, external input |

## Technical Context
### Existing Codebase
- `capture_realsense.py`: `capture_single_frame()` → `(depth_uint16_480x640, color_bgr_480x640x3)`
- `sam-3d-objects/notebook/inference.py`: `Inference(config_path)` → `__call__(image, mask, pointmap=None)` → dict with `rotation`, `translation`, `scale`, `gaussian`
- `inference_pipeline_pointmap.py`: `compute_pointmap(image, pointmap=None)` — accepts external pointmap
- `inference_utils.py:465`: `pose_decoder()` → returns `{translation: instance_position_l2c, rotation: instance_quaternion_l2c, scale: instance_scale_l2c}`
- PyTorch3D quaternion convention: (w, x, y, z)
- SAM 3D camera convention: PyTorch3D (needs conversion to standard camera frame)
- `camera_to_pytorch3d_camera()` in inference_pipeline_pointmap.py defines the R3↔PyTorch3D transform

### Key Implementation Details
**Method A (Hybrid):**
1. Run SAM 3D with MoGe (no pointmap injection) → get rotation quaternion
2. Convert quaternion (w,x,y,z) → RPY using scipy (with PyTorch3D→camera frame conversion)
3. Use RealSense depth + intrinsics + mask → deproject to 3D points → compute centroid → x,y,z in meters

**Method B (Pointmap injection):**
1. Convert RealSense depth + intrinsics → 3D pointmap (H,W,3) in camera frame
2. Apply `camera_to_pytorch3d_camera()` transform to match SAM 3D's expected convention
3. Pass pointmap to `inference(image, mask, pointmap=pointmap_tensor)`
4. Extract rotation + translation from output, convert to x,y,z,r,p,y

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| RealSense Camera | external system | depth(uint16 mm), color(BGR 640x480), intrinsics(fx,fy,cx,cy) | Produces RGB Image, Depth Image |
| RGB Image | core domain | pixels(H,W,3), dtype(uint8) | Input to SAM 3D Pipeline |
| Depth Image | core domain | values(H,W), dtype(uint16), unit(mm) | Used for Pointmap or Centroid |
| Segmentation Mask | core domain | binary(H,W), dtype(bool) | Selects object region |
| Pointmap | core domain | points(H,W,3), coordinate_system(camera/pytorch3d) | Input to SAM 3D (Method B) |
| SAM 3D Pipeline | core domain | Inference class, MoGe depth, pose_decoder | Produces Object Pose |
| Object Pose (6DoF) | core domain | x,y,z(meters), roll,pitch,yaw(degrees) | Output of pipeline |
| 3D Centroid | supporting | position(x,y,z meters) | Computed from Depth + Mask (Method A) |
| PoseEstimator | core domain | methods(hybrid, pointmap), config_path | Wraps SAM 3D Pipeline |

## Ontology Convergence

| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|-------------|-----|---------|--------|----------------|
| 1 | 7 | 7 | - | - | - |
| 2 | 8 | 1 | 0 | 7 | 88% |
| 3 | 8 | 0 | 0 | 8 | 100% |
| 4 | 9 | 1 | 0 | 8 | 89% |
| 5 | 9 | 0 | 0 | 9 | 100% |
| 6 | 9 | 0 | 0 | 9 | 100% |

## Interview Transcript
<details>
<summary>Full Q&A (6 rounds)</summary>

### Round 1
**Q:** RealSense의 metric depth를 pointmap으로 변환하여 SAM 3D에 직접 주입할 건가요, 아니면 SAM 3D 내장 MoGe depth를 그대로 사용하고 RealSense depth는 별도 용도로만 쓸 건가요?
**A:** MoGe + RealSense depth 하이브리드
**Ambiguity:** 55.7% (Goal: 0.65, Constraints: 0.30, Criteria: 0.20, Context: 0.60)

### Round 2
**Q:** 이 파이프라인의 출력을 어떻게 사용할 계획인가요?
**A:** 로봇 픽앤플레이스 타겟
**Ambiguity:** 42.8% (Goal: 0.75, Constraints: 0.35, Criteria: 0.50, Context: 0.65)

### Round 3
**Q:** Segmentation mask는 어떻게 생성하나요?
**A:** 외부에서 마스크 입력 (pre-generated)
**Ambiguity:** 34.8% (Goal: 0.85, Constraints: 0.45, Criteria: 0.55, Context: 0.70)

### Round 4 (Contrarian Mode)
**Q:** SAM 3D의 pose 추정은 MoGe monocular depth 기반으로 학습되었습니다. 더 단순한 접근(MoGe rotation + RealSense xyz)이 더 적합할 수 있지 않을까요?
**A:** 두 방식 모두 구현해서 비교
**Ambiguity:** 27.3% (Goal: 0.90, Constraints: 0.60, Criteria: 0.60, Context: 0.75)

### Round 5
**Q:** 출력 형식은 어떻게 되어야 하나요?
**A:** Python dict / dataclass
**Ambiguity:** 21.5% (Goal: 0.90, Constraints: 0.75, Criteria: 0.65, Context: 0.80)

### Round 6
**Q:** 파이프라인의 실행 형태는?
**A:** import 가능한 모듈/클래스
**Ambiguity:** 15.2% (Goal: 0.95, Constraints: 0.80, Criteria: 0.75, Context: 0.85)

</details>
