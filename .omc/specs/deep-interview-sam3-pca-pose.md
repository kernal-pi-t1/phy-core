# Deep Interview Spec: SAM 3 Mask + RealSense Depth PCA 6DoF Pose Estimation

## Metadata
- Interview ID: sam3-pca-pose-001
- Rounds: 7
- Final Ambiguity Score: 17.1%
- Type: brownfield
- Generated: 2026-03-21
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.92 | 0.35 | 0.322 |
| Constraint Clarity | 0.80 | 0.25 | 0.200 |
| Success Criteria | 0.70 | 0.25 | 0.175 |
| Context Clarity | 0.88 | 0.15 | 0.132 |
| **Total Clarity** | | | **0.829** |
| **Ambiguity** | | | **17.1%** |

## Goal
기존 `pose_estimator.py`(SAM 3D Objects 기반)를 **완전히 대체**하여, SAM 3 auto segmentation으로 마스크를 생성하고 RealSense depth point cloud에 PCA + gravity 보정을 적용하여 6DoF pose(x, y, z, roll, pitch, yaw)를 추정하는 Python 모듈을 구현한다. SAM 3D Objects 의존성을 제거한다.

## Pipeline
```
RealSense Camera
    ├── RGB image (640x480, BGR)
    └── Depth image (640x480, uint16 mm)
            │
            ▼
SAM 3 Auto Segmentation (sam3/ submodule)
    │   Input: RGB image
    │   Output: N개 object masks
    │
    ▼
Per-mask 6DoF Pose Estimation:
    1. Mask + Depth → 3D point cloud (deproject with intrinsics)
    2. PCA on point cloud → 3 eigenvectors (PC1=longest axis, PC3=shortest/normal)
    3. Gravity correction: Y-down 방향으로 rotation 보정 (테이블 위 물체 가정)
    4. Eigenvectors → Rotation matrix → RPY (degrees)
    5. Centroid of point cloud → x, y, z (meters)
    │
    ▼
Output: List[ObjectPose] (x, y, z meters, roll, pitch, yaw degrees)
```

## Constraints
- SAM 3 auto segmentation으로 전체 장면의 모든 물체 마스크 생성
- PCA로 orientation 계산 시 gravity 방향(Y-down) 보정 적용
- RealSense depth(uint16 mm)를 camera intrinsics로 3D deproject
- 기존 `capture_realsense.py`의 `capture_single_frame()` 활용
- SAM 3 submodule(`/home/robot/jm_ws/sam3/`) 활용
- GPU 사용 (SAM 3 inference)
- 출력 좌표계: OpenCV camera frame (X-right, Y-down, Z-forward)
- 다양한 형태의 물체 혼재 (대칭/비대칭 모두)
- 기존 `pose_estimator.py`를 완전히 대체 (SAM 3D Objects 의존성 제거)

## Non-Goals
- FoundationPose 구현 (이번 스코프에서 제외)
- ROS 통합 (Python 모듈로만 구현)
- 실시간 최적화
- 모델 학습/파인튜닝
- 로봇 모션 플래닝 통합

## Acceptance Criteria
- [ ] `pose_estimator.py`가 SAM 3 + PCA 방식으로 완전히 대체됨
- [ ] SAM 3D Objects (`sam-3d-objects/`) 의존성 완전 제거
- [ ] SAM 3 auto segmentation으로 장면 내 모든 물체 마스크 생성
- [ ] 각 마스크에 대해 RealSense depth → 3D point cloud → PCA → 6DoF pose
- [ ] PCA orientation에 gravity(Y-down) 보정 적용
- [ ] 출력: `List[ObjectPose]` (x,y,z meters, roll,pitch,yaw degrees, camera frame)
- [ ] `from pose_estimator import PoseEstimator`로 import 가능
- [ ] `__main__` 블록으로 standalone 테스트 가능
- [ ] `capture_realsense.py`와 호환 (640x480, uint16 depth, BGR color)
- [ ] Right-hand rule rotation matrix 보장 (det(R)=1)

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| SAM 3D Objects가 필요하다 | SAM 3 mask + depth PCA로 충분? | SAM 3D Objects 제거, SAM 3 + PCA로 대체 |
| FoundationPose도 필요하다 | 사용자가 scope 축소 | SAM 3 + PCA만 구현 |
| PCA만으로 orientation 충분 | 대칭 물체 문제 | PCA + gravity 보정으로 해결 |
| Mask는 외부 입력 | SAM 3 auto seg 사용 가능 | SAM 3 auto segmentation 내장 |
| 기존 코드 확장 | 완전 대체 vs 확장 | 기존 pose_estimator.py 완전 대체 |

## Technical Context
### 기존 코드 (대체 대상)
- `pose_estimator.py`: SAM 3D Objects 기반, `Inference` 클래스 사용, PyTorch3D quaternion → RPY 변환
- `capture_realsense.py`: `capture_single_frame()` → (depth_uint16, color_bgr) — 유지

### 재사용 가능한 유틸리티 함수
- `deproject_depth_to_points()`: depth + mask + intrinsics → 3D points (그대로 재사용)
- `compute_centroid()`: 3D points → centroid (그대로 재사용)
- `validate_inputs()`: 입력 검증 (수정하여 재사용)
- `ObjectPose` dataclass: 출력 형식 (그대로 재사용)

### 제거 대상
- SAM 3D Objects 관련 import (`from inference import Inference`)
- PyTorch3D convention 변환 (`quaternion_pytorch3d_to_rpy_camera`, `pointmap_camera_to_pytorch3d` 등)
- `depth_to_pointmap()` (SAM 3D에 주입하던 함수)
- `_estimate_hybrid()`, `_estimate_pointmap()` methods

### 새로 구현 필요
- SAM 3 auto segmentation wrapper (sam3/ submodule 활용)
- PCA orientation 계산 (eigenvectors → rotation matrix)
- Gravity 보정 (Y-down 방향으로 rotation 정렬)
- 다중 물체 처리 (auto seg → N masks → N poses)

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| RealSense Camera | external system | depth(uint16 mm), color(BGR 640x480), intrinsics(fx,fy,cx,cy) | Produces RGB Image, Depth Image |
| RGB Image | core domain | pixels(H,W,3), dtype(uint8) | Input to SAM 3 |
| Depth Image | core domain | values(H,W), dtype(uint16), unit(mm) | Used for Point Cloud |
| SAM 3 Segmentor | core domain | model, auto_mask_generator | Produces Segmentation Masks |
| Segmentation Mask | core domain | binary(H,W), dtype(bool), object_id | Selects object region |
| Point Cloud | core domain | points(N,3), coordinate_system(camera) | Input to PCA |
| PCA Orientation | supporting | eigenvectors(3,3), eigenvalues(3), gravity_corrected(bool) | Produces Rotation Matrix |
| Object Pose (6DoF) | core domain | x,y,z(meters), roll,pitch,yaw(degrees), method("sam3_pca") | Output per object |
| PoseEstimator | core domain | sam3_model, intrinsics | Wraps SAM 3 + PCA pipeline |

## Ontology Convergence

| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|-------------|-----|---------|--------|----------------|
| 1 | 8 | 8 | - | - | - |
| 2 | 9 | 1 | 0 | 8 | 89% |
| 3 | 9 | 0 | 0 | 9 | 100% |
| 4 | 9 | 0 | 0 | 9 | 100% |
| 5 | 9 | 0 | 1 | 8 | 100% |
| 6 | 8 | 0 | 0 | 8 | 100% |
| 7 | 9 | 1 | 0 | 8 | 89% |

## Interview Transcript
<details>
<summary>Full Q&A (7 rounds)</summary>

### Round 1
**Q:** 두 옵션(SAM 3 mask + PCA vs FoundationPose) 중 하나를 선택하려는 건가요, 아니면 둘 다 구현해서 비교하려는 건가요?
**A:** 둘 다 구현해서 비교
**Ambiguity:** 57.8% (Goal: 0.65, Constraints: 0.25, Criteria: 0.20, Context: 0.55)

### Round 2
**Q:** SAM 3 + PCA 방식에서 PCA로 orientation을 계산할 때, 대칭적인 물체는 PCA로 회전 축을 구분하기 어렵습니다. 피킹 대상 물체는 어떤 형태인가요?
**A:** 다양한 형태 혼재
**Ambiguity:** 50.3% (Goal: 0.70, Constraints: 0.40, Criteria: 0.25, Context: 0.60)

### Round 3
**Q:** 3가지 방식을 어떻게 비교/평가할 건가요? 성공 기준은 무엇인가요?
**A:** 실제 로봇 pick 성공률
**Ambiguity:** 40.3% (Goal: 0.75, Constraints: 0.45, Criteria: 0.50, Context: 0.65)

### Round 4 (Contrarian Mode)
**Q:** FoundationPose는 CAD 모델 또는 참조 이미지가 필요합니다. CAD 모델이 있나요?
**A:** 아직 미정 / 둘 다 시도 → **사용자 인터럽트: SAM 3만 구현**
**Ambiguity:** 36.5% (Goal: 0.80, Constraints: 0.50, Criteria: 0.50, Context: 0.70)

### Round 5
**Q:** SAM 3로 mask를 생성할 때 어떤 프롬프트 방식을 사용하나요?
**A:** Auto (전체 세그먼테이션)
**Ambiguity:** 30.3% (Goal: 0.85, Constraints: 0.60, Criteria: 0.55, Context: 0.75)

### Round 6
**Q:** 기존 pose_estimator.py를 어떻게 할 건가요?
**A:** 기존 대체 (SAM 3D Objects 제거)
**Ambiguity:** 22.0% (Goal: 0.92, Constraints: 0.80, Criteria: 0.70, Context: 0.88)

### Round 7 (Simplifier Mode)
**Q:** PCA eigenvector → rotation matrix 구성 방식은?
**A:** PCA + gravity 방향 보정
**Ambiguity:** 17.1% (Goal: 0.92, Constraints: 0.80, Criteria: 0.70, Context: 0.88)

</details>
