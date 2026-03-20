# SAM3 Test Scripts

SAM3 관련 기능을 독립적으로 테스트하는 스크립트 모음.

## 사용법

```bash
cd /home/robot/jm_ws

# 1. Segmentation만 테스트 (RealSense 캡처 → SAM3 → 마스크 시각화)
python3 sam3_test/test_segmentation.py

# 2. Pose estimation 테스트 (SAM3 + depth PCA → 6DoF)
python3 sam3_test/test_pose.py

# 3. ROS2 서비스 호출 테스트 (sam3_node 실행 중 필요)
#    터미널 1: ros2 launch phy_core phy_core.launch.py
#    터미널 2:
python3 sam3_test/test_service_call.py              # default: "object"
python3 sam3_test/test_service_call.py cup bottle    # 여러 prompt
```

## 출력

결과 이미지는 `sam3_test/output/`에 저장됩니다.
