# SAM3 Test Scripts

sam3_node와 동일한 코드 경로(`phy_core.sam3`)를 사용하는 독립 테스트 스크립트.

## 사용법

```bash
cd /home/robot/jm_ws

# 0. Crop 영역 설정 (최초 1회)
python3 sam3_test/select_crop_region.py
python3 sam3_test/select_crop_region.py --image sam3_test/output/01_input.png

# 1. Segmentation 테스트 (Sam3FastProcessor — node와 동일)
python3 sam3_test/test_segmentation.py          # threshold=0.01
python3 sam3_test/test_segmentation.py 0.1      # threshold 지정

# 2. Pose estimation 테스트 (PoseEstimator — node와 동일)
python3 sam3_test/test_pose.py

# 3. ROS2 서비스 호출 테스트 (sam3_node 실행 중 필요)
#    터미널 1: ros2 launch phy_core phy_core.launch.py
#    터미널 2:
python3 sam3_test/test_service_call.py              # default: "object"
python3 sam3_test/test_service_call.py cup bottle    # 여러 prompt
```

## 출력

결과 이미지는 `sam3_test/output/`에 저장됩니다.

| 스크립트 | 출력 파일 |
|----------|----------|
| test_segmentation | `01_input.png`, `02_overlay_crop.png`, `03_overlay_full.png` |
| test_pose | `pose_input.png`, `pose_result.png` |

## 설정 파일

- `crop_config.yaml` (workspace root) — `select_crop_region.py`로 생성, segmentation/pose 모두 적용
