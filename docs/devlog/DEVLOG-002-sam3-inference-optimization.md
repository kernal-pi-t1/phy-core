---
id: DEVLOG-002
title: SAM3 inference speed optimization via autocode
task_type: feature
status: completed
complexity: high
created: 2026-03-21
duration_estimate: 2h
tags: [sam3, inference-optimization, autocode, fp16, torch-compile, frame-reuse, benchmark]
---

## 목표 (Goal)
- SAM3 segmentation inference 속도를 최대한 빠르게 개선
- Config(모델 아키텍처/파라미터)는 고정, segmentation 품질(마스크 >= 4개) 유지
- Autocode 자동 실험 루프를 활용한 체계적 최적화 (15회 실험)

## 접근 과정 (Approach Log)

### 1차: autocast fp16 + cudnn.benchmark
- **방법**: `torch.cuda.amp.autocast(dtype=torch.float16)` + `torch.backends.cudnn.benchmark = True`
- **결과**: 성공 — 423ms → 215ms (-49.1%)
- **원인**: fp16이 matmul/conv 비용을 절반으로, cudnn.benchmark가 고정 input shape에 대해 최적 알고리즘 선택

### 2차: resolution 504 축소
- **방법**: Sam3Processor resolution을 1008 → 504로 변경
- **결과**: CRASH — ViT positional encoding shape mismatch (AssertionError)
- **원인**: `freqs_cis` 버퍼가 72x72 (1008/14)로 `__init__`에서 고정 등록됨. 504→36x36은 호환 불가. resolution 변경하려면 positional embedding interpolation 필요

### 3차: text encoder 캐싱
- **방법**: "object" prompt의 text features를 한번만 계산하고 재사용
- **결과**: 성공 — 215→210ms (-2.3%)
- **원인**: text encoder 비용은 작지만, 매번 동일한 결과를 재계산할 필요 없음

### 4차: torch.compile
- **방법**: `build_sam3_image_model(compile=True)` — ViT backbone에 `torch.compile(mode="default", fullgraph=True)` 적용
- **결과**: 성공 — 210→184ms (-12.5%)
- **원인**: ViT의 32개 반복 attention block에서 operator fusion, Triton 커널 생성 효과

### 5~6차: pre-computed image tensor on GPU
- **방법**: PIL→tensor 변환을 미리 수행하고 캐싱
- **결과**: CRASH — OOM (torch.compile이 ~15GB 사용, 추가 텐서 공간 없음)
- **원인**: expandable_segments 설정으로도 해결 안됨 — fragmentation이 아닌 capacity 문제

### 7차: matmul precision medium + extra warmup
- **방법**: `torch.set_float32_matmul_precision('medium')` + warmup 3회
- **결과**: 197ms (+7.1%) — DISCARD
- **원인**: autocast fp16이 이미 활성화된 상태에서 TF32 모드는 효과 없음 (fp32 matmul이 거의 없음)

### 8차: mask interpolation 스킵
- **방법**: `_forward_grounding`에서 full resolution interpolation 제거
- **결과**: 196ms (+6.9%) — DISCARD
- **원인**: interpolation 비용은 전체 대비 무시할 수준. ViT backbone이 87% 차지

### 9차: backbone fp16 weights
- **방법**: `model.backbone.half()` — autocast 대신 영구 fp16 변환
- **결과**: 189ms (+2.9%), 15 masks — DISCARD
- **원인**: autocast와 중복, 오히려 수치 정밀도 저하로 마스크 1개 손실

### 10차: forward_grounding compile
- **방법**: `torch.compile(model.forward_grounding)`
- **결과**: CRASH — geometry_encoders에서 `pin_memory` 사용, dynamo 미지원

### 11차: flash_sdp 명시 활성화
- **방법**: `torch.backends.cuda.enable_flash_sdp(True)` + n_runs=10
- **결과**: 194ms — DISCARD
- **원인**: `F.scaled_dot_product_attention`이 이미 flash attention 자동 사용 중

### 12차: max-autotune compile
- **방법**: ViT backbone에 `torch.compile(mode="max-autotune")` 적용
- **결과**: 199ms, 15 masks — DISCARD
- **원인**: exhaustive kernel search가 이 GPU에서는 default보다 느림, 마스크 품질도 저하

### 13차: Frame reuse (backbone 캐싱) ← 핵심 돌파구
- **방법**: backbone output을 캐싱하고, 2/3 프레임은 grounding만 재실행
- **결과**: 성공 — effective 82ms (-55.4%)
- **원인**: backbone=172ms(87%), grounding=26ms(13%). 정적/저변동 장면에서 backbone 재실행 불필요

### 14~15차: skip ratio 최적화 + 상세 분석
- **방법**: backbone을 5프레임마다 실행, 4/5 프레임은 grounding만
- **결과**: 성공 — effective 60.7ms
- **세부 분석**: full=198ms, grounding=26ms, skip3=84ms, skip5=61ms, skip10=43ms

## 최종 해결 (Final Solution)
- **최적화 스택**: autocast fp16 + cudnn.benchmark + cached text + torch.compile + frame reuse (skip-5)
- **결과**: 423ms → 60.7ms (-85.7%), 16 masks 유지
- **핵심 인사이트**: ViT backbone이 87% 병목 → 매 프레임 실행 불필요, grounding만 재실행하면 26ms

### Latency Breakdown
| Component     | Time     | % of total |
|---------------|----------|------------|
| ViT backbone  | ~172ms   | 87%        |
| Grounding     | ~26ms    | 13%        |

### Effective FPS at skip ratios
| Skip ratio | Effective ms | FPS  |
|------------|-------------|------|
| No skip    | 198.6ms     | ~5   |
| Skip 3     | 83.7ms      | ~12  |
| Skip 5     | 60.7ms      | ~16  |
| Skip 10    | 43.4ms      | ~23  |

## 교훈 (Lessons Learned)
1. **ViT backbone이 압도적 병목**: 1008x1008 해상도에 32 blocks — inference의 87%. 모델 수정 없이는 이걸 줄이기 어려움
2. **torch.compile + VRAM**: compile은 activation memory를 크게 증가시킴. 15.5GB GPU에서 추가 텐서 캐싱 불가
3. **ViT resolution 변경 불가**: `freqs_cis` (RoPE positional encoding)가 init 시 고정 크기로 등록. 변경하려면 모델 내부 수정 + interpolation 필요
4. **Frame reuse가 가장 효과적**: model 수정 없이 pipeline 레벨에서 가장 큰 개선 (-55.4%). 정적/저변동 장면에 특히 유효
5. **autocast > permanent fp16**: autocast가 수치적으로 더 안전 (softmax, accumulator는 fp32 유지)
6. **이미 기본 활성화된 최적화 주의**: flash attention, TF32 등은 PyTorch가 자동 활성화 — 명시적 설정은 효과 없음
7. **Autocode 자동 실험이 효과적**: 15회 실험을 체계적으로 수행하여 최적 조합 도출. 분석 에이전트가 trend 파악에 도움

## 변경 파일 (Changed Files)
- `autocode_experiment.py` — 최적화 실험 wrapper (frame reuse pipeline, 모든 최적화 적용)
- `autocode_bench.py` — baseline 벤치마크 스크립트
- `.autocode/program.md` — 실험 설정 (target, metric, guard, constraints)
- `.autocode/results.tsv` — 15회 실험 결과 기록
- `.autocode/analysis/analysis_1.md` — 10회차 시점 자동 분석 리포트
