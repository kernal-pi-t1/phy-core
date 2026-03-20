# Plan: ROS2 Pick-and-Place Orchestration System (Final)

## Source Spec
`.omc/specs/deep-interview-ros2-orchestration.md`

## Consensus Status
- **Iterations:** 2 (Planner v1 → Critic REVISE → Planner v2 → Architect APPROVE_WITH_IMPROVEMENTS → Critic APPROVE_WITH_IMPROVEMENTS)
- **All critical/major issues resolved**

## Requirements Summary

Build a ROS2 Humble Python package containing:
1. **orchestration_node** — State machine that receives JSON prompts via custom service and coordinates robot_node (existing action server) + sam3_node for pick-validate-place cycles
2. **sam3_node** — Wraps existing `PoseEstimator` (`pose_estimator.py:184`) and `capture_single_frame` (`capture_realsense.py:5`) as ROS2 service server with two services
3. **Custom interfaces** — .msg, .srv definitions for inter-node communication

## RALPLAN-DR Summary

### Principles
1. **Minimal wrapping** — Reuse `PoseEstimator.estimate_poses()` (`pose_estimator.py:204`) which already encapsulates SAM3 segmentation + PCA pose estimation internally. No separate mask extraction needed.
2. **Clean state machine** — Orchestration logic as explicit states with clear transitions
3. **Interface-first** — Define .msg/.srv interfaces before implementing nodes
4. **Config-driven waypoints** — Fixed poses (init, val, place, place_return) loaded from ROS2 parameters
5. **Separation of concerns** — Orchestration owns flow; sam3_node owns perception; robot_node owns motion

### Decision Drivers
1. **ROS2 Humble compatibility** — ament_cmake for interfaces, ament_python for nodes
2. **Existing robot_node contract** — Must discover and match robot_node's existing action type
3. **Threading model** — MultiThreadedExecutor with dual callback groups (MutuallyExclusive for service server, Reentrant for clients)

### Viable Options

#### Option A: Single ament_cmake package with ament_cmake_python
- **Invalidation:** ament_cmake_python requires manual Python install rules and doesn't support `entry_points` / `console_scripts`. For Python-only nodes, ament_python is the standard and better-supported approach.

#### Option B: Two packages — interfaces (ament_cmake) + nodes (ament_python) [Chosen]
- **Why chosen:** ROS2 Humble requires ament_cmake with rosidl for custom interface generation. Python nodes are best served by ament_python. This is the canonical ROS2 pattern.

## Package Structure

```
jm_ws/src/
├── pick_place_interfaces/          # ament_cmake package
│   ├── package.xml
│   ├── CMakeLists.txt
│   ├── msg/
│   │   └── ObjectPose.msg
│   └── srv/
│       ├── PickPlaceTask.srv       # Orchestration entry point
│       ├── GetPickPose.srv         # sam3: object_name → ObjectPose
│       └── ValidateObject.srv      # sam3: object_name → is_valid
│
└── pick_place_orchestration/       # ament_python package
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── resource/pick_place_orchestration
    ├── pick_place_orchestration/
    │   ├── __init__.py
    │   ├── orchestration_node.py   # State machine + action client + service clients
    │   └── sam3_node.py            # Service server wrapping PoseEstimator
    ├── launch/
    │   └── orchestration.launch.py
    └── config/
        └── waypoints.yaml
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
string error_message
```

### GetPickPose.srv (sam3_node)
```
# Request
string object_name
---
# Response
bool success
pick_place_interfaces/ObjectPose pose
string error_message
```

### ValidateObject.srv (sam3_node)
```
# Request
string object_name
---
# Response
bool is_valid
```

**NOTE on robot_node action:** The orchestration_node must connect to the existing robot_node's action server. The action type is NOT defined in this package — it must match whatever robot_node already provides. See Step 0 for discovery.

## Implementation Steps

### Step 0: Discover robot_node's action interface
1. Run `ros2 node info <robot_node_name>` to find advertised action servers
2. Run `ros2 action list -t` to identify the action type
3. Run `ros2 interface show <action_type>` to get the goal/result/feedback structure
4. Document the action type, goal fields, and result fields
5. Add the action type's package as a dependency in orchestration package.xml
6. **If robot_node is not yet running**, coordinate with the robot team to get the action type definition. This blocks implementation of orchestration_node's action client.

### Step 1: Create interface package (`pick_place_interfaces`)
1. Create `jm_ws/src/pick_place_interfaces/`
2. `package.xml`: ament_cmake, build dep `rosidl_default_generators`, exec dep `rosidl_default_runtime`
3. `CMakeLists.txt`: `rosidl_generate_interfaces()` for ObjectPose.msg, PickPlaceTask.srv, GetPickPose.srv, ValidateObject.srv
4. Build and verify: `colcon build --packages-select pick_place_interfaces`
5. Verify: `ros2 interface show pick_place_interfaces/srv/PickPlaceTask`

### Step 2: Create orchestration Python package
1. Create `jm_ws/src/pick_place_orchestration/`
2. `package.xml`: ament_python, exec deps: `rclpy`, `pick_place_interfaces`, robot_node's action package
3. `setup.py` with `console_scripts`:
   - `orchestration_node = pick_place_orchestration.orchestration_node:main`
   - `sam3_node = pick_place_orchestration.sam3_node:main`
4. `setup.cfg`: install directories for launch and config

### Step 3: Implement sam3_node (`pick_place_orchestration/sam3_node.py`)

**Key insight:** `PoseEstimator.estimate_poses()` at `pose_estimator.py:204` already encapsulates the full pipeline:
- Takes `(rgb_or_bgr, depth_mm, intrinsics, prompt)` as input
- Internally calls `Sam3Processor.set_image()` + `set_text_prompt()` for segmentation (lines 229-230)
- Extracts masks, deprojection, PCA rotation, centroid (lines 232-261)
- Returns `List[ObjectPose]`

**No separate SAM3 invocation or mask extraction is needed.**

Implementation:
1. Import `PoseEstimator` from `pose_estimator` (`pose_estimator.py:184`)
2. Import `capture_single_frame` from `capture_realsense` (`capture_realsense.py:5`)
3. Node initialization:
   - Create `PoseEstimator(device="cuda", confidence_threshold=0.5)` — loads SAM3 model (~10-30s)
   - Declare parameters: `device` (string, default "cuda"), `confidence_threshold` (float, default 0.5)
   - Camera intrinsics: declare parameters `fx`, `fy`, `cx`, `cy` as **mandatory** ROS2 parameters (no default). Read from YAML config. Alternatively, sam3_node may query intrinsics at startup by opening a temporary `pyrealsense2` pipeline: `pipe.start() → profile.get_stream().as_video_stream_profile().get_intrinsics() → pipe.stop()`.
   - Use a `threading.Lock` to serialize access to PoseEstimator (SAM3 GPU model is not thread-safe)
4. Service server `get_pick_pose` (GetPickPose.srv):
   ```python
   def get_pick_pose_callback(self, request, response):
       try:
           with self._lock:
               depth_mm, color_bgr = capture_single_frame()
               intrinsics = (self.fx, self.fy, self.cx, self.cy)
               poses = self._estimator.estimate_poses(
                   color_bgr, depth_mm, intrinsics,
                   prompt=request.object_name, is_bgr=True
               )
           if poses:
               p = poses[0]  # Take first detection
               response.success = True
               response.pose.x, response.pose.y, response.pose.z = p.x, p.y, p.z
               response.pose.roll, response.pose.pitch, response.pose.yaw = p.roll, p.pitch, p.yaw
           else:
               response.success = False
               response.error_message = f"No object '{request.object_name}' detected"
       except Exception as e:
           self.get_logger().error(f"get_pick_pose failed: {e}")
           response.success = False
           response.error_message = str(e)
       return response
   ```
5. Service server `validate_object` (ValidateObject.srv):
   ```python
   def validate_object_callback(self, request, response):
       try:
           with self._lock:
               depth_mm, color_bgr = capture_single_frame()
               intrinsics = (self.fx, self.fy, self.cx, self.cy)
               poses = self._estimator.estimate_poses(
                   color_bgr, depth_mm, intrinsics,
                   prompt=request.object_name, is_bgr=True
               )
           response.is_valid = len(poses) > 0  # Object detected = valid
       except Exception as e:
           self.get_logger().error(f"validate_object failed: {e}")
           response.is_valid = False
       return response
   ```
   **Validation algorithm:** Calls `estimate_poses()` with the object name. Returns `is_valid=True` if the result list is non-empty (object successfully detected in gripper at val_pose position).

### Step 4: Implement orchestration_node (`pick_place_orchestration/orchestration_node.py`)

**Threading model (CRITICAL):** Must use `MultiThreadedExecutor` with **dual callback groups**:
- `MutuallyExclusiveCallbackGroup` for the `pick_place_task` service server — ensures only one task runs at a time (prevents concurrent pick-place cycles if two requests arrive simultaneously)
- `ReentrantCallbackGroup` for outbound clients (action client, service clients) — allows blocking calls inside the service callback without deadlock

```python
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

class OrchestrationNode(Node):
    def __init__(self):
        super().__init__('orchestration_node')
        # Separate callback groups for concurrency control
        self._task_cb_group = MutuallyExclusiveCallbackGroup()  # One task at a time
        self._client_cb_group = ReentrantCallbackGroup()         # Non-blocking clients

        self._task_service = self.create_service(
            PickPlaceTask, 'pick_place_task',
            self.task_callback, callback_group=self._task_cb_group)
        self._robot_action_client = ActionClient(
            self, <RobotActionType>, '<robot_action_name>',
            callback_group=self._client_cb_group)
        self._get_pose_client = self.create_client(
            GetPickPose, 'get_pick_pose',
            callback_group=self._client_cb_group)
        self._validate_client = self.create_client(
            ValidateObject, 'validate_object',
            callback_group=self._client_cb_group)

        # Wait for sam3_node services at startup
        self._get_pose_client.wait_for_service(timeout_sec=60.0)
        self._validate_client.wait_for_service(timeout_sec=60.0)

def main():
    rclpy.init()
    node = OrchestrationNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
```

**Why dual callback groups?** `ReentrantCallbackGroup` on the service server would allow concurrent `task_callback` executions — two simultaneous PickPlaceTask requests would both try to control the robot. `MutuallyExclusiveCallbackGroup` on the service server ensures only one pick-place cycle runs at a time. `ReentrantCallbackGroup` on the clients allows the blocked service callback to make outbound calls (action goals, service requests) without deadlock.

**Parameters for fixed waypoints** (loaded from YAML config):
- `init_pose`: [x, y, z, roll, pitch, yaw]
- `val_pose`: [x, y, z, roll, pitch, yaw]
- `place_pose`: [x, y, z, roll, pitch, yaw]
- `place_return_pose`: [x, y, z, roll, pitch, yaw]

**State machine implementation:**

States: `IDLE`, `INIT_POSE`, `GET_PICK_POSE`, `PICK_POSE`, `VAL_POSE`, `VALIDATE`, `PLACE_POSE`, `PLACE_RETURN`

```
task_callback(request, response):
    store object_name = request.object_name
    store return_reason = request.return_reason
    retry_count = 0

    while True:
        # 1. Move to init pose
        result = send_robot_action(self.init_pose)
        if not result.success:
            response.success = False
            response.error_message = "robot_node failed: init_pose"
            return response

        # 2. Get pick pose from sam3
        pose_resp = call_service(get_pick_pose, object_name)
        if not pose_resp.success:
            response.success = False
            response.error_message = f"sam3 get_pick_pose failed: {pose_resp.error_message}"
            return response

        # 3. Move to pick pose (dynamic)
        result = send_robot_action(pose_resp.pose)
        if not result.success:
            response.success = False
            response.error_message = "robot_node failed: pick_pose"
            return response

        # 4. Move to validation pose
        result = send_robot_action(self.val_pose)
        if not result.success:
            response.success = False
            response.error_message = "robot_node failed: val_pose"
            return response

        # 5. Validate object
        val_resp = call_service(validate_object, object_name)

        if val_resp.is_valid:
            # 6a. SUCCESS PATH: place object
            result = send_robot_action(self.place_pose)
            if not result.success:
                response.success = False
                response.error_message = "robot_node failed: place_pose"
                return response
            # Return to init
            result = send_robot_action(self.init_pose)
            if not result.success:
                response.success = False
                response.error_message = "robot_node failed: return to init_pose after place"
                return response
            response.success = True
            return response
        else:
            # 6b. RETRY PATH: return defective item and retry
            retry_count += 1
            self.get_logger().warn(
                f"Validation failed for '{object_name}', retry attempt {retry_count}")
            result = send_robot_action(self.place_return_pose)
            if not result.success:
                response.success = False
                response.error_message = "robot_node failed: place_return"
                return response
            # Loop continues: goto init_pose → get_pick_pose → ...
            # Reuses stored object_name for retry
```

**Failure handling:**
- robot_node action failure (any step) → abort immediately, return `success=False` with error message
- sam3_node get_pick_pose failure (no object detected) → abort, return `success=False`
- sam3_node service communication failure → ROS2 service call exception → abort
- Concurrent request → serialized by MutuallyExclusiveCallbackGroup (second request queues until first completes)

### Step 5: Create launch file and config

**`launch/orchestration.launch.py`:**
- Launch sam3_node and orchestration_node
- Set environment variables:
  - `PYTHONPATH` append `/home/robot/jm_ws` (for `pose_estimator`, `capture_realsense` imports)
  - `PYTHONPATH` append `/home/robot/jm_ws/sam3` (for `sam3` package — needed by `pose_estimator.py:194`)
- Load waypoints from `config/waypoints.yaml`
- Pass camera intrinsics as parameters

**`config/waypoints.yaml`:**
```yaml
orchestration_node:
  ros__parameters:
    init_pose: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    val_pose: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    place_pose: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    place_return_pose: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

sam3_node:
  ros__parameters:
    device: "cuda"
    confidence_threshold: 0.5
    fx: 615.0    # RealSense D435 typical value — REPLACE with actual
    fy: 615.0
    cx: 320.0
    cy: 240.0
```

### Step 6: Build and test
1. `colcon build --packages-select pick_place_interfaces pick_place_orchestration`
2. Verify interfaces: `ros2 interface list | grep pick_place`
3. Unit test: mock `PoseEstimator` and `capture_single_frame` to test sam3_node service logic
4. Unit test: mock action client + service clients to test orchestration_node state machine transitions (happy path + retry path + failure path)
5. Integration test: launch both nodes, mock robot_node action server, send PickPlaceTask request

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| robot_node action type unknown | High | **Blocker** | Step 0: discover via ros2 CLI before implementation |
| PoseEstimator import fails (sys.path) | Medium | High | Launch file sets PYTHONPATH; includes /home/robot/jm_ws and /home/robot/jm_ws/sam3 |
| SAM3 model loading slow (~10-30s) | High | Medium | Loaded once at sam3_node startup; subsequent calls fast |
| RealSense camera open/close per call | Medium | Medium | Known limitation per Principle 1 (~200ms warmup). Acceptable for pick-and-place. |
| SAM3 GPU model not thread-safe | Medium | High | threading.Lock in sam3_node serializes access |
| Camera intrinsics not configured | Medium | High | Mandatory ROS2 parameters; provide typical D435 defaults in YAML as reference |
| Concurrent PickPlaceTask requests | Low | High | MutuallyExclusiveCallbackGroup on service server serializes requests |
| Camera/GPU exception during service call | Medium | Medium | try/except in sam3_node callbacks; return success=False with error |

## Verification Steps
1. `colcon build` succeeds with zero errors for both packages
2. `ros2 interface show pick_place_interfaces/srv/PickPlaceTask` shows correct fields
3. `ros2 interface show pick_place_interfaces/srv/GetPickPose` shows correct fields
4. `ros2 interface show pick_place_interfaces/srv/ValidateObject` shows correct fields
5. Launch both nodes: `ros2 launch pick_place_orchestration orchestration.launch.py`
6. Verify services advertised: `ros2 service list | grep -E "(pick_place_task|get_pick_pose|validate_object)"`
7. Test happy path: mock robot_node → call PickPlaceTask → validate returns true → success=true
8. Test retry path: mock robot_node → validate returns false first, true second → success=true after retry
9. Test failure path: sam3 detects no object → success=false with error_message
10. Test concurrent requests: two simultaneous PickPlaceTask calls → second queues, both complete sequentially

## Acceptance Criteria
- [ ] `colcon build --packages-select pick_place_interfaces pick_place_orchestration` succeeds
- [ ] orchestration_node advertises `pick_place_task` service (PickPlaceTask.srv)
- [ ] sam3_node advertises `get_pick_pose` (GetPickPose.srv) and `validate_object` (ValidateObject.srv) services
- [ ] orchestration_node connects to robot_node action server as client
- [ ] Fixed waypoints (init, val, place, place_return) loaded from ROS2 parameters / YAML config
- [ ] sam3_node `get_pick_pose` calls `PoseEstimator.estimate_poses()` with text prompt, returns first pose
- [ ] sam3_node `validate_object` calls `PoseEstimator.estimate_poses()` with object_name, returns true if detected
- [ ] State machine: init → get_pick → pick → val → validate(true) → place → init → response(success=true)
- [ ] State machine: validate(false) → place_return → init → get_pick → retry (infinite until success)
- [ ] State machine: robot_node failure at ANY step → abort with success=false + error_message
- [ ] State machine: sam3 detection failure → abort with success=false + error_message
- [ ] MultiThreadedExecutor with dual callback groups (MutuallyExclusive for service, Reentrant for clients)
- [ ] sam3_node uses threading.Lock to serialize PoseEstimator access
- [ ] sam3_node service callbacks wrapped in try/except for camera/GPU exceptions
- [ ] No modification to existing pose_estimator.py or capture_realsense.py
- [ ] PYTHONPATH set correctly in launch file
- [ ] orchestration_node waits for sam3_node services at startup (wait_for_service)

## ADR: Architecture Decision Record

### Decision
Two-package ROS2 Humble system: `pick_place_interfaces` (ament_cmake) + `pick_place_orchestration` (ament_python) with sam3_node wrapping `PoseEstimator.estimate_poses()` directly.

### Drivers
1. ROS2 Humble requires ament_cmake + rosidl for custom interface generation
2. `PoseEstimator.estimate_poses()` already encapsulates SAM3 segmentation + pose estimation — no separate mask pipeline needed
3. Orchestration_node must avoid deadlock when making blocking calls inside service callback
4. Concurrent request safety requires MutuallyExclusiveCallbackGroup on service server

### Alternatives Considered
1. **Single ament_cmake package**: Rejected — ament_cmake_python lacks console_scripts support
2. **Separate mask extraction (sam3_inference + RLE decode)**: Rejected — PoseEstimator already handles this internally
3. **SingleThreadedExecutor with async callbacks**: Rejected — complex, error-prone
4. **ReentrantCallbackGroup for all callbacks**: Rejected — allows concurrent task_callback executions, causing robot conflicts

### Why Chosen
Option B follows canonical ROS2 pattern. Direct `estimate_poses()` call respects Principle 1 (minimal wrapping). Dual callback groups provide both deadlock safety and mutual exclusion.

### Consequences
- Must discover robot_node's action type before implementation (Step 0)
- Camera pipeline opens/closes per call (~200ms overhead)
- SAM3 model loads at startup (~10-30s)
- threading.Lock serializes perception calls

### Follow-ups
- Finalize robot_node action client after action type discovery
- Configure actual camera intrinsics and waypoints for production
- Consider persistent RealSense pipeline if cycle time is a concern

## Changelog
### v1 → v2
1. Fixed PoseEstimator API: `estimate_poses()` (plural, line 204), class at line 184, constructor takes `device`+`confidence_threshold`
2. Removed separate mask extraction — PoseEstimator handles SAM3 internally
3. Added Step 0: discover robot_node action type
4. Mandated MultiThreadedExecutor
5. Added object_name to ValidateObject.srv
6. Defined validation algorithm
7. Added failure transitions with error_message
8. Added threading.Lock for thread safety
9. Specified PYTHONPATH in launch file

### v2 → Final (consensus improvements)
10. **Dual callback groups:** Split into MutuallyExclusiveCallbackGroup (service server) + ReentrantCallbackGroup (clients) to prevent concurrent task execution while avoiding deadlock
11. **Final init_pose error check:** Added failure check on `send_robot_action(self.init_pose)` in success path (was missing in v2 line 282)
12. **Retry counter:** Added `retry_count` with logging for operational observability
13. **Exception handling:** Added try/except in sam3_node service callbacks for camera/GPU failures
14. **wait_for_service:** orchestration_node waits for sam3_node services at startup
15. **Camera intrinsics clarified:** Made mandatory parameters (no ambiguous auto-detect claim); provided typical D435 values as reference
