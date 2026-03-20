# Plan: ROS2 Pick-and-Place Orchestration System

## Source Spec
`.omc/specs/deep-interview-ros2-orchestration.md`

## Requirements Summary

Build a ROS2 Humble Python package containing:
1. **orchestration_node** — State machine that receives JSON prompts via custom service and coordinates robot_node (existing action server) + sam3_node for pick-validate-place cycles
2. **sam3_node** — Wraps existing `pose_estimator.py` and `capture_realsense.py` as ROS2 service server with two services: `get_pick_pose` and `validate_object`
3. **Custom interfaces** — .msg, .srv, .action definitions for inter-node communication

## RALPLAN-DR Summary

### Principles
1. **Minimal wrapping** — Reuse existing Python modules (`pose_estimator.py:215` PoseEstimator, `capture_realsense.py:5` capture_single_frame) without modification
2. **Clean state machine** — Orchestration logic as explicit states with clear transitions, not nested callbacks
3. **Interface-first** — Define .msg/.srv/.action interfaces before implementing nodes
4. **Config-driven waypoints** — Fixed poses (init, val, place, place_return) loaded from ROS2 parameters, not hardcoded
5. **Separation of concerns** — Orchestration owns flow control; sam3_node owns perception; robot_node owns motion

### Decision Drivers
1. **ROS2 Humble compatibility** — Must use rclpy, colcon, ament_python or ament_cmake for interfaces
2. **Existing robot_node contract** — robot_node already exists with custom .action; orchestration must be action client
3. **Single-threaded simplicity** — No concurrent picks; one object at a time, sequential flow

### Viable Options

#### Option A: Single package with interfaces + nodes (Recommended)
- **Approach:** One ROS2 package `pick_place_orchestration` containing both interfaces (msg/srv/action) and Python nodes
- **Pros:** Simple build, single colcon package, easy to deploy
- **Cons:** Interface changes require full package rebuild; mixed ament_cmake (for interfaces) + ament_python (for nodes) in same package is not recommended by ROS2 conventions
- **Note:** Actually, ROS2 best practice requires interfaces in a separate `_interfaces` or `_msgs` package (ament_cmake) because msg/srv/action generation needs CMake. Nodes go in a separate ament_python package.

#### Option B: Two packages — interfaces + nodes (Recommended, revised)
- **Approach:** `pick_place_interfaces` (ament_cmake, .msg/.srv/.action) + `pick_place_orchestration` (ament_python, nodes)
- **Pros:** ROS2 best practice; clean separation; interface changes don't force node rebuild; reusable interfaces
- **Cons:** Two packages to maintain; slightly more setup
- **This is the standard ROS2 pattern and recommended approach.**

**Invalidation of Option A:** ROS2 Humble does not support generating custom interfaces (.msg/.srv/.action) in ament_python packages. Interface generation requires ament_cmake with rosidl. Mixing both in one package is fragile and not officially supported.

## Package Structure

```
jm_ws/src/
├── pick_place_interfaces/          # ament_cmake package
│   ├── package.xml
│   ├── CMakeLists.txt
│   ├── msg/
│   │   └── ObjectPose.msg          # 6DoF pose message
│   ├── srv/
│   │   ├── PickPlaceTask.srv       # Orchestration entry point (object + return_reason → success)
│   │   ├── GetPickPose.srv         # sam3: object_name → ObjectPose
│   │   └── ValidateObject.srv     # sam3: → success (bool)
│   └── action/
│       └── MoveToPose.action       # robot_node action (or match existing)
│
└── pick_place_orchestration/       # ament_python package
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── resource/pick_place_orchestration
    ├── pick_place_orchestration/
    │   ├── __init__.py
    │   ├── orchestration_node.py   # State machine + action client + service client
    │   └── sam3_node.py            # Service server wrapping PoseEstimator + capture_realsense
    ├── launch/
    │   └── orchestration.launch.py # Launch both nodes
    └── config/
        └── waypoints.yaml          # Fixed poses: init, val, place, place_return
```

## Interface Definitions

### ObjectPose.msg
```
float64 x       # meters
float64 y       # meters
float64 z       # meters
float64 roll    # degrees
float64 pitch   # degrees
float64 yaw     # degrees
```

### PickPlaceTask.srv (orchestration entry point)
```
# Request
string object_name
string return_reason
---
# Response
bool success
```

### GetPickPose.srv (sam3_node)
```
# Request
string object_name
---
# Response
bool success
pick_place_interfaces/ObjectPose pose
```

### ValidateObject.srv (sam3_node)
```
# Request (empty — sam3_node captures and validates internally)
---
# Response
bool is_valid
```

### MoveToPose.action (for robot_node — placeholder, must match existing)
```
# Goal
pick_place_interfaces/ObjectPose target_pose
---
# Result
bool success
---
# Feedback
float32 progress
```

**NOTE:** The MoveToPose.action definition must match whatever the existing robot_node expects. If robot_node already defines its action type, we use that instead and skip defining MoveToPose.action.

## Implementation Steps

### Step 1: Create workspace src/ directory and interface package
1. Create `jm_ws/src/pick_place_interfaces/` with package.xml (ament_cmake, build deps: rosidl_default_generators)
2. Create CMakeLists.txt with rosidl_generate_interfaces()
3. Define ObjectPose.msg, PickPlaceTask.srv, GetPickPose.srv, ValidateObject.srv
4. Optionally define MoveToPose.action if robot_node doesn't already define it

### Step 2: Create orchestration Python package
1. Create `jm_ws/src/pick_place_orchestration/` with package.xml (ament_python, exec deps: rclpy, pick_place_interfaces)
2. Create setup.py with console_scripts entry points for both nodes
3. Create package directory structure

### Step 3: Implement sam3_node
**File:** `pick_place_orchestration/sam3_node.py`
- Import from `pose_estimator` (`/home/robot/jm_ws/pose_estimator.py:215` PoseEstimator class)
- Import from `capture_realsense` (`/home/robot/jm_ws/capture_realsense.py:5` capture_single_frame)
- ROS2 node with two service servers:
  - `get_pick_pose`: calls capture_single_frame() → gets RGB+depth → needs segmentation mask from SAM3 agent → runs PoseEstimator.estimate_pose() → returns ObjectPose
  - `validate_object`: calls capture_single_frame() → runs SAM3 segmentation → determines if object is valid (present, correct, oriented) → returns bool
- Parameters: `sam3_config_path`, `pose_method` (hybrid/pointmap), `camera_intrinsics`
- Challenge: PoseEstimator needs a segmentation mask. The `call_sam_service` in `sam3/sam3/agent/client_sam3.py:51` takes `image_path` + `text_prompt` and returns segmentation results. sam3_node needs to: capture image → save temp file → call SAM3 segmentation → extract mask → run PoseEstimator.

### Step 4: Implement orchestration_node
**File:** `pick_place_orchestration/orchestration_node.py`
- State machine with states: IDLE, INIT_POSE, GET_PICK_POSE, PICK_POSE, VAL_POSE, VALIDATE, PLACE_POSE, PLACE_RETURN
- ROS2 node with:
  - Service server: `pick_place_task` (PickPlaceTask.srv) — entry point
  - Action client: connects to robot_node's action server
  - Service clients: `get_pick_pose`, `validate_object` (sam3_node)
- Parameters for fixed waypoints: `init_pose`, `val_pose`, `place_pose`, `place_return_pose` (each as [x,y,z,r,p,y])
- State machine transitions:
  1. IDLE → receive PickPlaceTask request → store object_name, return_reason
  2. INIT_POSE → send init_pose to robot_node action → wait for result
  3. GET_PICK_POSE → call sam3_node get_pick_pose service → receive pose
  4. PICK_POSE → send received pose to robot_node action → wait for result
  5. VAL_POSE → send val_pose to robot_node action → wait for result
  6. VALIDATE → call sam3_node validate_object service → get true/false
     - true → PLACE_POSE
     - false → PLACE_RETURN
  7. PLACE_POSE → send place_pose to robot_node action → wait → INIT_POSE → respond success=true
  8. PLACE_RETURN → send place_return to robot_node action → wait → INIT_POSE → goto GET_PICK_POSE (retry)

### Step 5: Create launch file and config
1. `launch/orchestration.launch.py` — launches orchestration_node + sam3_node with parameters
2. `config/waypoints.yaml` — default waypoint values

### Step 6: Build and test
1. `colcon build --packages-select pick_place_interfaces pick_place_orchestration`
2. Verify message generation: `ros2 interface show pick_place_interfaces/srv/PickPlaceTask`
3. Unit test: state machine transitions
4. Integration test: mock robot_node action server + test full cycle

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PoseEstimator import fails (sys.path issues) | Medium | High | Add jm_ws to PYTHONPATH in launch file; or install pose_estimator as package |
| SAM3 model loading slow on node startup | High | Medium | Lazy initialization on first service call; add startup readiness check |
| RealSense camera conflict (sam3_node + other nodes) | Medium | High | Ensure only sam3_node opens RealSense; use singleton pattern |
| robot_node action type mismatch | High | High | Make MoveToPose.action configurable; or discover robot_node's actual action type at runtime |
| Blocking service calls in orchestration_node | Medium | Medium | Use async service calls with callbacks; or use MultiThreadedExecutor |

## Verification Steps
1. `colcon build` succeeds with no errors
2. `ros2 interface list | grep pick_place` shows all defined interfaces
3. Launch both nodes: no crash, services/actions advertised
4. `ros2 service call /pick_place_task pick_place_interfaces/srv/PickPlaceTask "{object_name: 'cup', return_reason: 'defect'}"` triggers state machine
5. State machine progresses through all states in happy path (val=true)
6. State machine retries correctly in unhappy path (val=false → place_return → retry)

## Acceptance Criteria
- [ ] `colcon build --packages-select pick_place_interfaces pick_place_orchestration` succeeds
- [ ] orchestration_node advertises `pick_place_task` service
- [ ] sam3_node advertises `get_pick_pose` and `validate_object` services
- [ ] orchestration_node connects to robot_node action server as client
- [ ] Fixed waypoints loaded from ROS2 parameters / YAML config
- [ ] State machine executes full happy path: init → get_pick → pick → val → validate(true) → place → init → respond
- [ ] State machine executes retry path: validate(false) → place_return → init → get_pick → retry
- [ ] sam3_node internally uses PoseEstimator from pose_estimator.py and capture_single_frame from capture_realsense.py
- [ ] No modification to existing pose_estimator.py or capture_realsense.py
