# Deep Interview Spec: ROS2 Pick-and-Place Orchestration Node

## Metadata
- Interview ID: ros2-orch-001
- Rounds: 10
- Final Ambiguity Score: 18.1%
- Type: brownfield
- Generated: 2026-03-21
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.92 | 0.35 | 0.322 |
| Constraint Clarity | 0.82 | 0.25 | 0.205 |
| Success Criteria | 0.70 | 0.25 | 0.175 |
| Context Clarity | 0.78 | 0.15 | 0.117 |
| **Total Clarity** | | | **0.819** |
| **Ambiguity** | | | **18.1%** |

## Goal
ROS2 Humble 기반으로 두 개의 노드를 구현한다:

1. **orchestration_node** — 외부에서 커스텀 service로 JSON prompt(`object`, `return_reason`)를 받아, 기존 robot_node(action server)와 sam3_node를 조율하여 pick-validate-place 사이클을 수행하는 state machine 노드.

2. **sam3_node** — 기존 `pose_estimator.py` + `capture_realsense.py`를 ROS2 노드로 wrapping하여 두 가지 service를 제공:
   - `get_pick_pose`: object 이름을 받아 RealSense 카메라로 물건을 인식하고 pick할 6DoF pose 반환
   - `validate_object`: val_pose에서 RealSense 카메라로 물건을 확인하고 true/false 반환

### State Machine Flow
```
[Service 수신: JSON prompt {object, return_reason}]
    │
    ▼
[init_pose] ── action → robot_node (고정 waypoint)
    │
    ▼
[sam3_node: get_pick_pose] ── service call (object 이름 전달)
    │                          카메라로 인식 → 6DoF pose 반환
    ▼
[pick_pose] ── action → robot_node (sam3가 반환한 동적 pose)
    │
    ▼
[val_pose] ── action → robot_node (고정 waypoint)
    │
    ▼
[sam3_node: validate_object] ── service call
    │                            카메라로 검증 → true/false
    ├── true ──▶ [place_pose] ── action → robot_node (고정 waypoint)
    │                │
    │                ▼
    │           [init_pose] ── action → robot_node
    │                │
    │                ▼
    │           [Service response: success=true]
    │
    └── false ─▶ [place_return] ── action → robot_node (불량 반환 전용 고정 waypoint)
                     │
                     ▼
                [init_pose] ── action → robot_node
                     │
                     ▼
                [sam3_node: get_pick_pose] ── 재시도 (무제한 반복)
```

## Constraints
- **ROS2 Humble** (Python rclpy)
- **robot_node는 이미 존재**: 커스텀 .action 정의의 action server를 제공하는 기존 노드
- **sam3_node 신규 구현**: 기존 `pose_estimator.py` + `capture_realsense.py`를 wrapping
- **sam3_node가 RealSense 카메라를 직접 사용** (topic subscribe 아님)
- **Pose 분류**:
  - 동적(sam3가 결정): `pick_pose`만
  - 고정(config/파라미터): `init_pose`, `val_pose`, `place_pose`, `place_return`
- **JSON prompt 수신**: 커스텀 ROS2 service로 수신
  - Request: `object` (string), `return_reason` (string)
  - Response: `success` (bool)
- **재시도 제한 없음**: validation false 시 성공할 때까지 무한 반복
- **커스텀 인터페이스 필요**: .action (robot_node용), .srv (orchestration 진입점, sam3 service 2종), .msg (pose 전달용)

## Non-Goals
- robot_node 구현 (이미 존재)
- MoveIt 연동 (robot_node가 내부적으로 처리)
- 멀티 물건 동시 처리 (단건 순차 처리)
- 재시도 횟수 제한 / 타임아웃 로직
- GUI / 시각화

## Acceptance Criteria
- [ ] ROS2 Humble 패키지로 빌드 가능 (`colcon build` 성공)
- [ ] orchestration_node가 커스텀 service로 JSON prompt를 수신할 수 있음
- [ ] orchestration_node가 state machine 흐름대로 robot_node에 action을 순차 전송
- [ ] sam3_node의 get_pick_pose service가 object 이름을 받아 6DoF pose를 반환
- [ ] sam3_node의 validate_object service가 true/false를 반환
- [ ] validation false 시 place_return → init_pose → get_pick_pose 재시도 루프 동작
- [ ] validation true 시 place_pose → init_pose → service response(success=true) 반환
- [ ] 고정 waypoint(init, val, place, place_return)는 파라미터/config로 설정 가능
- [ ] 기존 pose_estimator.py, capture_realsense.py를 sam3_node에서 import하여 활용

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| 모든 pose가 동적 | "어떤 pose가 고정이고 동적인가?" | pick_pose만 동적, 나머지 4개 고정 |
| 재시도 제한 필요 | "무한 루프 위험" (Contrarian) | 사용자 결정: 제한 없이 성공까지 반복 |
| place_return = place 후 복귀 경로 | "place_return 역할?" | 불량 반환 전용 위치 (place_pose와 구분) |
| sam3_node가 topic으로 이미지 수신 | "카메라 직접 vs topic?" | sam3_node가 RealSense 직접 사용 |
| robot_node도 설계 필요 | "robot_node 존재 여부?" | 이미 존재하는 action server |

## Technical Context
### 기존 코드 (brownfield)
- `pose_estimator.py`: PoseEstimator 클래스 — RGB + depth + mask → 6DoF ObjectPose (x,y,z,roll,pitch,yaw)
  - hybrid / pointmap 두 가지 메서드 지원
  - sam3 inference 내부 호출
- `capture_realsense.py`: capture_single_frame() → (depth_mm, color_bgr)
- `sam3/sam3/agent/`: SAM3 agent 모듈 (client_sam3.py, agent_core.py)
- `librealsense/`: RealSense SDK (ROS2 package.xml 포함)

### 신규 구현 대상
- **ROS2 패키지**: 커스텀 interfaces (.msg, .srv, .action) + orchestration_node + sam3_node
- **orchestration_node**: rclpy 기반 state machine, action client + service client
- **sam3_node**: rclpy 기반 service server, 내부에서 PoseEstimator + capture_realsense 사용

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| orchestration_node | core domain | state, current_object, return_reason | action client → robot_node, service client → sam3_node |
| robot_node | external system | action server | receives action goals from orchestration_node |
| sam3_node | core domain | pose_estimator, realsense | provides get_pick_pose, validate_object services |
| JSON prompt | input | object (string), return_reason (string) | triggers orchestration_node via service |
| pick_pose | dynamic value | 6DoF (x,y,z,r,p,y) | returned by sam3_node, sent to robot_node |
| init_pose | static config | 6DoF or joint values | loaded from parameter |
| val_pose | static config | 6DoF or joint values | loaded from parameter |
| place_pose | static config | 6DoF or joint values | loaded from parameter |
| place_return | static config | 6DoF or joint values | 불량 반환 전용 위치 |
| validation_result | value | bool (true/false) | returned by sam3_node validate_object |
| realsense_camera | external system | RGB, depth, intrinsics | used internally by sam3_node |

## Ontology Convergence

| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|-------------|-----|---------|--------|----------------|
| 1 | 6 | 6 | - | - | - |
| 2 | 7 | 1 | 0 | 6 | 86% |
| 3 | 8 | 1 | 0 | 7 | 88% |
| 4 | 9 | 1 | 0 | 8 | 89% |
| 5 | 9 | 0 | 0 | 9 | 100% |
| 6 | 10 | 1 | 0 | 9 | 90% |
| 7 | 10 | 0 | 0 | 10 | 100% |
| 8 | 10 | 0 | 0 | 10 | 100% |
| 9 | 11 | 1 | 0 | 10 | 91% |
| 10 | 11 | 0 | 0 | 11 | 100% |

## Interview Transcript
<details>
<summary>Full Q&A (10 rounds)</summary>

### Round 1
**Q:** val_pose에서 sam3_node가 true를 반환한 경우, place_pose로 물건을 놓은 뒤 place_return으로 이동하나요? place_return의 역할이 정확히 무엇인가요?
**A:** place_return = 반환(불량) 경로 전용
**Ambiguity:** 66.0% (Goal: 0.55, Constraints: 0.20, Criteria: 0.15, Context: 0.40)

### Round 2
**Q:** sam3_node와의 통신 방식은? 새로 만들어야 하는지, 이미 존재하는지?
**A:** sam3_node도 같이 설계해줘
**Ambiguity:** 59.8% (Goal: 0.60, Constraints: 0.35, Criteria: 0.15, Context: 0.45)

### Round 3
**Q:** robot_node의 pose들은 고정 waypoint인가 동적인가?
**A:** pick_pose만 동적, 나머지 고정
**Ambiguity:** 51.7% (Goal: 0.70, Constraints: 0.50, Criteria: 0.15, Context: 0.50)

### Round 4 (Contrarian Mode)
**Q:** 재시도 횟수 제한 없이 무한 루프에 빠질 수 있는데, 종료 조건은?
**A:** 제한 없음 (성공할 때까지)
**Ambiguity:** 43.8% (Goal: 0.75, Constraints: 0.55, Criteria: 0.35, Context: 0.50)

### Round 5
**Q:** robot_node의 action server는 이미 존재하는가, 같이 설계해야 하는가?
**A:** robot_node는 이미 존재 (action server)
**Ambiguity:** 38.8% (Goal: 0.80, Constraints: 0.60, Criteria: 0.40, Context: 0.55)

### Round 6 (Simplifier Mode)
**Q:** robot_node action server의 goal 타입은?
**A:** 커스텀 .action 정의
**Ambiguity:** 33.8% (Goal: 0.85, Constraints: 0.65, Criteria: 0.45, Context: 0.60)

### Round 7
**Q:** JSON prompt를 받는 방식은? ROS2 topic, service, action?
**A:** ROS2 커스텀 service
**Ambiguity:** 30.5% (Goal: 0.85, Constraints: 0.70, Criteria: 0.50, Context: 0.65)

### Round 8
**Q:** JSON prompt의 구체적 필드는?
**A:** object + return_reason 두 필드만
**Ambiguity:** 26.3% (Goal: 0.90, Constraints: 0.75, Criteria: 0.55, Context: 0.65)

### Round 9
**Q:** sam3_node는 RealSense를 직접 사용하나, topic으로 이미지를 받나?
**A:** sam3_node가 RealSense 직접 사용
**Ambiguity:** 22.3% (Goal: 0.90, Constraints: 0.80, Criteria: 0.60, Context: 0.75)

### Round 10
**Q:** 오케스트레이션 완료 후 service response 포맷과 패키지 이름은?
**A:** bool만 반환
**Ambiguity:** 18.1% (Goal: 0.92, Constraints: 0.82, Criteria: 0.70, Context: 0.78)

</details>
