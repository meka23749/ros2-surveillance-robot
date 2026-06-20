# ROS2 Surveillance Robot

Autonomous industrial surveillance robot built with ROS2 Jazzy — camera perception, OpenCV anomaly detection and autonomous STOP/CONTINUE decisions.

## Architecture

robot_navigator     → moves robot between waypoints, publishes /robot/pose

camera_sensor       → generates simulated camera images, publishes /camera/image_raw

anomaly_detector    → OpenCV detection, publishes /detection/result

surveillance_manager → autonomous decisions, publishes /robot/command


## ROS2 Topics

| Topic | Type | Publisher | Subscriber |
|-------|------|-----------|------------|
| /robot/pose | Pose2D | robot_navigator | camera_sensor, surveillance_manager |
| /camera/image_raw | Image | camera_sensor | anomaly_detector |
| /detection/result | String (JSON) | anomaly_detector | surveillance_manager |
| /robot/command | String | surveillance_manager | robot_navigator |

## Quick start

```bash
# Install ROS2 Jazzy + dependencies
sudo apt install ros-jazzy-desktop ros-jazzy-cv-bridge ros-jazzy-vision-opencv

# Build
source /opt/ros/jazzy/setup.bash
colcon build --packages-select surveillance_robot
source install/setup.bash

# Launch all nodes
ros2 launch surveillance_robot surveillance.launch.py
```

## Autonomous behavior


Camera detects anomaly (red shape = defect)

↓

AnomalyDetector publishes confidence score

↓

SurveillanceManager decision:

confidence > 0.3 → STOP robot at current position

zone clear       → CONTINUE patrol

↓

RobotNavigator executes command


## Bugs found and fixed

1. **Confidence threshold too high** — surveillance_manager had threshold 0.5 but detector reported 0.48, causing all anomalies to be missed. Fixed by lowering threshold to 0.3.
2. **flake8 import order** — multiple I100/I201/Q000 errors detected by CI across all nodes. Fixed iteratively through 3 fix commits.

## CI/CD

GitHub Actions runs on every push to main:
- ROS2 Jazzy setup
- colcon build
- colcon test (flake8, pep257, copyright)

## Author

Steve Meka
