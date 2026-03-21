# phy_core

ROS2 Pick-Validate-Place 오케스트레이션 패키지. SAM3 비전 인식 + Doosan 로봇 제어 + VLM 검증을 통합하여 자율 피킹 사이클을 수행합니다.

## Architecture

```
┌──────────────┐    Json.srv     ┌────────────────────┐    Move.action    ┌──────────────────┐
│   Client     │ ──────────────> │  phy_core_node     │ ───────────────>  │  action_node     │
│  (외부 요청)  │                │  (Orchestration)   │                   │  (Robot Motion)  │
└──────────────┘                └────────┬───────────┘                   └──────────────────┘
                                         │                                  ├─ MoveLine (IK)
                              GetPose /  │  VlmJudge                        ├─ MoveJoint (FK)
                           CountObjects  │                                  └─ Gripper Control
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
                   ┌──────┴──────┐              ┌──────┴──────┐
                   │  sam3_node  │              │  vlm_node   │
                   │ (Perception)│              │(Validation) │
                   └─────────────┘              └─────────────┘
```

### Nodes

| Node | Description | Entry Point |
|------|-------------|-------------|
| `phy_core_node` | 상태 머신 기반 오케스트레이터 (pick-validate-place 사이클) | `phy_core.node.phy_core_node:main` |
| `sam3_node` | SAM3 기반 6DoF 포즈 추정 서비스 (get_pose, count_objects) | `phy_core.node.sam3_node:main` |
| `vlm_node` | VLM 기반 파지 상태 검증 서비스 | `phy_core.node.vlm_node:main` |
| `action_node` | Doosan 로봇 모션 액션 서버 (MoveLine/MoveJoint + Gripper) | `phy_core.node.action_node:main` |

### Interfaces

| Type | Name | Description |
|------|------|-------------|
| Service | `GetPose` | SAM3 객체 검출 + 6DoF 포즈 반환 |
| Service | `CountObjects` | SAM3 검출 객체 수 반환 (파지 검증용) |
| Service | `Json` | 오케스트레이션 태스크 요청 (payload = 객체명) |
| Service | `VlmJudge` | VLM 기반 파지/손상 상태 판정 |
| Action | `Move` | 로봇 이동 + 그리퍼 제어 (FK/IK method 선택) |

## Installation

### Prerequisites

- ROS2 Humble
- Doosan Robot ROS2 Driver (`dsr_msgs2`)
- Intel RealSense SDK + `pyrealsense2`
- CUDA-capable GPU (SAM3 inference)

### Build

```bash
# 워크스페이스 루트에서
cd ~/jm_ws

# phy_interface 먼저 빌드 (서비스/액션 메시지)
colcon build --packages-select phy_interface
source install/setup.bash

# phy_core 빌드
colcon build --packages-select phy_core
source install/setup.bash
```

### Product Image Registration

SAM3 검출 대상 제품 이미지를 등록합니다.

```bash
# 제품 등록
python3 src/phy_core/register_product.py --image /path/to/product.png --name "콜라"

# 커스텀 프롬프트와 함께 등록
python3 src/phy_core/register_product.py --image /path/to/product.png --name "콜라" --prompt "cola bottle"

# 등록된 제품 목록
python3 src/phy_core/register_product.py --list

# 제품 삭제
python3 src/phy_core/register_product.py --delete "콜라"
```

## Usage

### Launch (Full System)

모든 노드를 한번에 실행합니다 (sam3_node, vlm_node, phy_core_node).

```bash
ros2 launch phy_core phy_core.launch.py
```

### Individual Nodes

```bash
# SAM3 Perception Node
ros2 run phy_core sam3_node --ros-args --params-file src/phy_core/config/waypoints.yaml

# VLM Validation Node
ros2 run phy_core vlm_node

# Orchestration Node
ros2 run phy_core phy_core_node --ros-args --params-file src/phy_core/config/waypoints.yaml

# Action Node (Robot Motion Server) - 베이스 좌표계
ros2 run phy_core action_node

# Action Node - 툴 좌표계
ros2 run phy_core action_node --ros-args -p frame:=tool
```

### Commands

#### Pick-Place Task 요청

```bash
# 객체명으로 pick-place 사이클 시작
ros2 service call /pick_place_task phy_interface/srv/Json "{payload: '콜라'}"
```

#### Robot Motion (Action Goal)

```bash
# IK (베이스 좌표계 절대 위치) 이동 + 그리퍼 닫기
ros2 action send_goal /pose_to_joint phy_interface/action/Move \
    "{target_pose: [500.0, 0.0, 400.0, 0.0, 180.0, 0.0], grip: true, method: 'ik'}"

# FK (조인트 각도) 이동
ros2 action send_goal /pose_to_joint phy_interface/action/Move \
    "{target_pose: [0.0, 0.0, 90.0, 0.0, 90.0, 0.0], grip: false, method: 'fk'}"

# 툴 좌표계 상대 이동 (Z +10mm)
ros2 action send_goal /pose_to_joint phy_interface/action/Move \
    "{target_pose: [0.0, 0.0, 10.0, 0.0, 0.0, 0.0], grip: false, method: 'ik'}"
```

#### SAM3 Perception 직접 호출

```bash
# 객체 포즈 추정
ros2 service call /get_pose phy_interface/srv/GetPose "{method: '콜라'}"

# 객체 수 카운트
ros2 service call /count_objects phy_interface/srv/CountObjects "{method: '콜라'}"
```

#### 상태 모니터링

```bash
# 토픽 목록 확인
ros2 topic list

# 그리퍼 토크 모니터링
ros2 topic echo /dsr01/gripper/torque

# 노드 상태 확인
ros2 node list
ros2 node info /orchestration_node
```

## Configuration

`config/waypoints.yaml`에서 로봇 웨이포인트와 카메라 파라미터를 설정합니다.

```yaml
orchestration_node:
  ros__parameters:
    # 카메라 외부 파라미터 (base frame 기준)
    camera_offset: [0.80, 0.0, 0.66]    # [x, y, z] meters
    camera_rpy: [180.0, 0.0, 0.0]       # [roll, pitch, yaw] degrees

    # 웨이포인트 - joint angles [j1~j6] degrees (FK/MoveJoint)
    init_pose: [0.0, 0.0, 90.0, 0.0, 90.0, 0.0]
    val_pose: [0.0, -10.0, 90.0, 0.0, 90.0, 0.0]
    place_pose: [90.0, 0.0, 90.0, 0.0, 90.0, 0.0]
    place_return_pose: [-90.0, 0.0, 90.0, 0.0, 90.0, 0.0]

sam3_node:
  ros__parameters:
    device: "cuda"
    confidence_threshold: 0.0054
    frame_skip: 1
    # 카메라 내부 파라미터 (RealSense D435)
    fx: 260.0
    fy: 593.0
    cx: 115.0
    cy: 443.0
```

## Testing

### Unit Tests 실행

```bash
# 전체 테스트 실행
cd ~/jm_ws
python3 -m pytest src/phy_core/test/ -v

# 개별 테스트 파일 실행
python3 -m pytest src/phy_core/test/test_orchestration_node.py -v
python3 -m pytest src/phy_core/test/test_sam3_node.py -v
python3 -m pytest src/phy_core/test/test_action_node.py -v

# 특정 테스트 클래스만 실행
python3 -m pytest src/phy_core/test/test_orchestration_node.py::TestOrchestrationNodeTaskCallback -v

# 특정 테스트 함수만 실행
python3 -m pytest src/phy_core/test/test_action_node.py::TestExecuteCallback::test_fk_mode_calls_move_joint -v
```

### colcon test로 실행

```bash
colcon build --packages-select phy_core
colcon test --packages-select phy_core --event-handlers console_direct+
colcon test-result --all
```

### Test Coverage

| Test File | Target Node | Test Cases |
|-----------|-------------|------------|
| `test_orchestration_node.py` | `phy_core_node` | 상태 상수, 초기화, get_pose, send_move, 태스크 콜백 (성공/실패/재시도), 좌표 변환 |
| `test_sam3_node.py` | `sam3_node` | 초기화, 카메라 intrinsics 검증, 콜백 (검출/미검출/예외), 스레드 안전성 |
| `test_action_node.py` | `action_node` | 초기화, goal accept/reject, cancel, MoveLine/MoveJoint, 그리퍼 제어, FK/IK 분기, 피드백 |

### SAM3 Threshold Sweep

```bash
# confidence_threshold 최적값 탐색
cd ~/jm_ws
python3 sam3_test/sweep_threshold.py
```

## State Machine Flow

```
IDLE → INIT_POSE → GET_PICK_POSE → PICK_EXECUTE → VAL_POSE → VALIDATE → PLACE_POSE → IDLE
                                        │                         │              │
                                        │ (torque < 30)           │ (recheck     │ (VLM fail)
                                        ↓                         │  count >= 3) ↓
                                      IDLE                        ↓         PLACE_RETURN
                                                            retry (loop)      → retry (loop)
```

1. **INIT_POSE**: FK로 초기 위치 이동 + 그리퍼 열기
2. **GET_PICK_POSE**: SAM3로 객체 6DoF 포즈 추정 (camera → base 좌표 변환)
3. **PICK_EXECUTE**: Pre-grasp → Descend → Grip → Torque 검증 → Lift
4. **VAL_POSE**: SAM3 recheck (잔여 객체 수로 파지 성공 확인)
5. **VALIDATE**: VLM으로 파지 상태/손상 여부 검증
6. **PLACE_POSE / PLACE_RETURN**: 검증 결과에 따라 배치 또는 반환 후 재시도
