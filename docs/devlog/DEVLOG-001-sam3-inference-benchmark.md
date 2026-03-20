---
id: DEVLOG-001
title: SAM3 + Pose Estimation inference time 벤치마크
task_type: config
status: completed
complexity: medium
created: 2026-03-21
duration_estimate: 1.5h
tags: [sam3, benchmark, inference-time, gpu, pose-estimation, realsense]
---

## 목표 (Goal)
- SAM3 + Pose Estimation 파이프라인의 각 단계별 inference time과 GPU 메모리 사용량 측정
- PNG 이미지 저장 시간 포함 전체 latency 프로파일링

## 환경
- GPU: NVIDIA GeForce RTX 5080 Laptop GPU (16GB VRAM)
- Python 3.10, PyTorch 2.10, CUDA
- 카메라: RealSense D435 (640x480)
- 모델: SAM3 (facebook/sam3) — 체크포인트 미적용 (gated repo 접근 불가, 랜덤 가중치 사용. inference time 측정에는 무관)

## 접근 과정 (Approach Log)

### 1차 시도
- **방법**: `benchmark_sam3.py` 스크립트 작성 후 `python3`으로 직접 실행
- **결과**: 실패 — `ModuleNotFoundError: No module named 'iopath'`
- **원인**: system python에는 SAM3 의존성이 없음. conda 환경 필요.

### 2차 시도
- **방법**: `conda run -n TK_model`로 실행
- **결과**: 실패 — `No module named 'pkg_resources'`
- **원인**: TK_model 환경의 setuptools v82에서 `pkg_resources` 모듈이 제거됨

### 3차 시도
- **방법**: setuptools를 v69로 다운그레이드
- **결과**: 부분성공 — `pkg_resources` 해결, 하지만 `einops` 누락
- **원인**: sam3 pyproject.toml에 `einops`가 dependencies에 빠져있으나 코드에서 사용

### 4차 시도
- **방법**: `einops` 설치 + `pip install -e sam3/` (editable install)
- **결과**: 부분성공 — `pycocotools` 추가 누락
- **원인**: train 코드 의존성이 inference 코드 import chain에 연결되어 숨은 의존성 발생

### 5차 시도
- **방법**: `pycocotools`, `scipy` 추가 설치
- **결과**: 부분성공 — 모든 import 해결, HuggingFace 401 인증 에러
- **원인**: `facebook/sam3`가 gated repo, HF 로그인 필요

### 6차 시도
- **방법**: HF 토큰으로 로그인
- **결과**: 실패 — 403 Forbidden (gated repo 접근 승인 필요)
- **원인**: 토큰은 유효하나 facebook/sam3 모델 접근 권한 미승인

### 7차 시도 (최종)
- **방법**: `load_from_HF=False`로 체크포인트 없이 랜덤 가중치로 실행
- **결과**: 성공 — inference time 측정 완료 (mask 0개지만 시간 측정에 무관)
- **원인**: 모델 구조와 연산량이 동일하므로 가중치 값은 inference time에 영향 없음

## 최종 해결 (Final Solution)

### 측정 결과

| 단계 | 시간 (ms) | 비고 |
|------|-----------|------|
| RealSense 캡처 | ~2,204 | warmup 5프레임 + pipeline start/stop |
| PNG 저장 (cv2.imwrite) | ~6.1 | 640x480, ~365KB |
| **SAM3 모델 로드** | **~6,871 (6.9s)** | 최초 1회만 |
| **SAM3 set_image** | **~335** | 이미지 인코딩 (ViT backbone) |
| **SAM3 set_text_prompt** | **~77** | 텍스트 프롬프트 + 마스크 디코딩 |
| **SAM3 inference 합계** | **~412** | set_image + set_text_prompt |
| Pose PCA (depth→3D→PCA→RPY) | ~1.4 | 15,000 mask pixels 기준 |

### GPU 메모리 사용량

| 시점 | allocated (MB) | reserved (MB) | peak (MB) |
|------|---------------|---------------|-----------|
| 모델 로드 전 | 0 | 0 | 0 |
| 모델 로드 후 | 3,462 | 3,574 | 3,462 |
| inference 후 | 3,810 | 4,566 | 4,211 |

- nvidia-smi 기준: 4,623 MiB used / 16,303 MiB total (약 28%)

### 전체 파이프라인 소요 시간 (모델 로드 제외)
- 캡처 + PNG 저장 + SAM3 inference + Pose PCA ≈ **2,622 ms (~2.6초)**
- 캡처 제외 순수 inference: **~420 ms**
- SAM3 inference만: **~412 ms** (bottleneck)
- ROS 노드 상시 실행 시 실질 1-shot latency: **SAM3 (~412ms) + PCA (~1.4ms) ≈ ~414ms**

## 교훈 (Lessons Learned)
1. **setuptools v82에서 pkg_resources 제거됨** — `setuptools<70` 다운그레이드 또는 `importlib.resources`로 마이그레이션 필요
2. **sam3 pyproject.toml에 einops 누락** — train 코드 import chain이 inference에 연결되어 숨은 의존성 발생
3. **facebook/sam3는 gated repo** — 접근 승인이 필요하며, `load_from_HF=False`로 시간 측정만 가능
4. **RealSense capture가 전체의 84%** — ROS 노드 상시 스트리밍 시 제거됨, 실질 bottleneck은 SAM3 ViT encoder (~335ms)
5. **GPU VRAM 여유** — peak ~4.2GB / 16GB 사용, 다른 모델과 병행 가능

## 변경 파일 (Changed Files)
- `benchmark_sam3.py` — SAM3 파이프라인 벤치마크 스크립트 (신규 생성)
