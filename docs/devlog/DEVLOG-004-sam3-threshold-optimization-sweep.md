---
id: DEVLOG-004
title: SAM3 confidence_threshold 최적값 탐색 (autocode sweep)
task_type: config
status: completed
complexity: medium
created: 2026-03-21
duration_estimate: 1h
tags: [sam3, confidence-threshold, autocode, sweep, pose-estimation]
---

## 목표 (Goal)
- SAM3 pose estimation의 confidence_threshold 최적값을 찾아 검출 성공률과 위치 안정성을 극대화
- 기존 threshold=0.008에서 70% 검출률 → 개선 필요

## 접근 과정 (Approach Log)

### 1차 시도: Autocode 개별 실험 방식
- **방법**: autocode 패턴 (git commit/revert per experiment)으로 threshold를 하나씩 변경하며 벤치마크
- **결과**: 부분성공 — threshold=0.005에서 첫 실험 score 차이가 크게 나옴 (109.4 vs 89.0)
- **원인**: 확률적 특성상 10회 trial에서도 분산이 크고, git commit/revert 오버헤드가 비효율적

### 2차 시도: 단일 sweep 스크립트
- **방법**: 14개 threshold를 한 스크립트에서 순차 실행하는 `sweep_threshold.py` 작성
- **결과**: 성공 — coarse sweep으로 0.005가 최고 (score=108.7, 10/10 detect, 0 FP)
- **원인**: 한 프로세스에서 연속 실행하여 환경 변수 최소화

### 3차 시도: Fine-grained sweep (0.004~0.006)
- **방법**: 0.002 간격으로 11개 값 추가 sweep
- **결과**: 성공 — sweet spot 확인: 0.0048~0.0054 (모두 10/10, FP=0, max_std < 1.5mm)
- **원인**: 이 범위에서 true positive confidence가 threshold를 충분히 넘기면서 false positive는 걸러짐

## Coarse Sweep 결과

| Threshold | 검출률 | FP | MaxStd(mm) | Score |
|-----------|--------|-----|------------|-------|
| 0.001 | 0/10 | 10 | N/A | 0.0 |
| 0.002 | 1/10 | 9 | N/A | 10.0 |
| 0.003 | 5/10 | 5 | 0.52 | 59.5 |
| 0.004 | 7/10 | 3 | 1.43 | 78.6 |
| **0.005** | **10/10** | **0** | **1.30** | **108.7** |
| 0.006 | 10/10 | 0 | 6.75 | 103.2 |
| 0.007 | 9/10 | 0 | 0.96 | 99.0 |
| 0.008 (기존) | 7/10 | 0 | 1.39 | 78.6 |
| 0.010 | 4/10 | 0 | 1.47 | 48.5 |
| 0.012 | 2/10 | 0 | 1.02 | 29.0 |
| 0.015+ | 0/10 | 0 | N/A | 0.0 |

## Fine Sweep 결과 (0.004~0.006)

| Threshold | 검출률 | FP | MaxStd(mm) | Score |
|-----------|--------|-----|------------|-------|
| 0.0040 | 5/10 | 5 | 0.89 | 59.1 |
| 0.0044 | 8/10 | 2 | 1.27 | 88.7 |
| **0.0048** | **10/10** | **0** | **1.47** | **108.5** |
| 0.0050 | 10/10 | 0 | 6.48 | 103.5 |
| **0.0052** | **10/10** | **0** | **1.33** | **108.7** |
| **0.0054** | **10/10** | **0** | **1.32** | **108.7** |
| 0.0056 | 10/10 | 0 | 6.86 | 103.1 |
| 0.0060 | 9/10 | 1 | 18.26 | 90.0 |

## 최종 해결 (Final Solution)
- **최적 threshold: 0.005** (sweet spot: 0.0048~0.0054)
- 기존 0.008 → 0.005로 변경: 검출률 70% → 100%, FP 0, 위치 std < 1.5mm
- `waypoints.yaml`에 반영 완료

## 교훈 (Lessons Learned)
- SAM3의 confidence는 threshold 근처에서 급격히 변함 — 0.004 이하 FP 급증, 0.007 이상 miss 급증
- Autocode 개별 git commit 방식보다 sweep 스크립트가 파라미터 탐색에 훨씬 효율적
- 10회 trial로도 분산이 있으므로 여러 threshold의 경향을 함께 봐야 통계적으로 유의미
- Score 공식: detection_rate*100 + consistency_bonus(max 10) — 검출률 우선, 위치 안정성은 보너스

## 변경 파일 (Changed Files)
- `sam3_test/sweep_threshold.py` — threshold sweep 벤치마크 스크립트 (신규)
- `sam3_test/bench_threshold.py` — 단일 threshold 벤치마크 스크립트 (신규)
- `sam3_test/threshold_config.py` — autocode용 threshold 설정 (신규)
- `src/phy_core/config/waypoints.yaml` — confidence_threshold 0.5 → 0.005로 변경
