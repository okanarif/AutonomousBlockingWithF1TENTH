# Autonomous Blocking with F1TENTH

A full-stack autonomous racing system that detects opponent vehicles and executes **dynamic blocking strategies** using a F1TENTH scale racing car. The system combines real-time YOLO-based perception with a multi-raceline state machine controller running on ROS 2.

<p align="center">
  <img src="Project_Video.gif" alt="Autonomous Blocking Demo" width="800"/>
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1dHCisX2FVivGmcXfnGM-q2lspUNsZh6f/view">
    🎬 Watch Full Video
  </a>
</p>

---

## Overview

The car continuously localizes itself on a known map, detects the opponent using a ZED camera and a fine-tuned YOLOv8 model, and selects one of three pre-computed racelines depending on the opponent's position — blocking, neutral, or racing line.

```
┌──────────────────────────────────────────────────────┐
│                    System Pipeline                   │
│                                                      │
│  ZED Camera ──► YOLO Detector ──► State Machine      │
│                                        │             │
│  Particle Filter (Localization)        ▼             │
│       │                         Raceline Select      │
│       └────────────────────────► Pure Pursuit        │
│                                        │             │
│                                        ▼             │
│                                   AckDrive Command   │
└──────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
AutonomousBlockingWithF1TENTH/
├── AutonomousBlocking/              # ROS 2 workspace & control stack
│   ├── lab_ws25/
│   │   ├── src/
│   │   │   ├── state_machine/       # Dynamic raceline switching logic
│   │   │   ├── pure_pursuit/        # Path-following controller + racelines
│   │   │   ├── particle_filter/     # Localization (map-based)
│   │   │   ├── opponent_detection/  # YOLO ROS 2 node
│   │   │   └── sensors/             # ZED camera publisher
│   │   ├── launch/
│   │   │   └── full_system.launch.py
│   │   └── scripts/                 # Standalone utility scripts
│   ├── Raceline_Generation/         # Raceline generation scripts
│   ├── Opponent_Detection_Train/    # Standalone YOLO training (legacy)
│   ├── setup_env.sh                 # Environment setup for the robot
│   └── train.py / test.py / video.py
│
├── Perception Opponent Training/    # YOLO training pipeline
│   ├── sensors/                     # ROS 2 camera package
│   ├── perception/                  # ROS 2 perception package
│   ├── scripts/                     # Inference & data collection scripts
│   ├── dataset/                     # Labeled training data
│   │   ├── images/
│   │   └── labels/
│   └── runs/                        # YOLO training outputs
│
├── video_to_gif.py                  # Utility: convert MP4 → GIF
├── Project_Video.gif                # Demo GIF
└── README.md
```

---

## Components

### State Machine
Monitors the opponent's detected position and switches among three racelines:
- **Raceline 1** — Default racing line
- **Raceline 2** — Blocking line (cuts off opponent)
- **Raceline 3** — Defensive wide line

### Pure Pursuit
Classic geometric path-following controller. Tracks the active raceline and publishes `AckermannDriveStamped` commands to the vehicle.

### Particle Filter
Map-based Monte Carlo localization. Uses LiDAR scans and a pre-built occupancy grid to estimate the car's pose in real time.

### Opponent Detection (YOLO)
A YOLOv8n model fine-tuned on F1TENTH car images. Runs on-board (GPU) via a ROS 2 node that subscribes to `/camera/image_raw` and publishes detections on `/opponent_detections`.

### Sensors
ZED stereo camera driver packaged as a ROS 2 node, publishing raw images at configurable resolution and frame rate.

---

## Quick Start

### 1. Clone & Navigate

```bash
git clone https://github.com/your-username/AutonomousBlockingWithF1TENTH.git
cd AutonomousBlockingWithF1TENTH/AutonomousBlocking/lab_ws25
```

### 2. Install Dependencies

```bash
# ROS 2 packages
sudo apt-get install \
  ros-humble-vision-msgs \
  ros-humble-cv-bridge \
  ros-humble-rqt-image-view

# Python packages
pip install torch torchvision ultralytics opencv-python pillow
```

### 3. Build the Workspace

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select sensors opponent_detection state_machine pure_pursuit particle_filter
source install/setup.bash
```

### 4. Launch the Full System

```bash
# Set environment (fixes PyTorch ARM64 OpenMP issue)
source ../../setup_env.sh

# Launch everything in one command
ros2 launch launch/full_system.launch.py
```

Or launch each component separately:

```bash
# Terminal 1 – Localization
ros2 launch particle_filter localize_launch.py

# Terminal 2 – Camera
ros2 launch sensors camera.launch.py

# Terminal 3 – Opponent Detection
ros2 launch opponent_detection opponent_detector.launch.py

# Terminal 4 – State Machine
ros2 launch state_machine state_machine.launch.py

# Terminal 5 – Pure Pursuit
ros2 launch pure_pursuit pure_pursuit_launch.py
```

---

## Training the Perception Model

```bash
cd "Perception Opponent Training"

# Train YOLOv8 on the opponent car dataset
python3 train.py

# Evaluate on test images
python3 test.py

# Run real-time inference on ZED camera
python3 scripts/zed_realtime_detection.py
```

---

## ROS 2 Topics

| Topic | Message Type | Description |
|---|---|---|
| `/camera/image_raw` | `sensor_msgs/Image` | Raw ZED camera feed |
| `/opponent_detections` | `vision_msgs/Detection2DArray` | Detected opponent bounding boxes |
| `/opponent_detections/visualization` | `sensor_msgs/Image` | Annotated camera image |
| `/drive` | `ackermann_msgs/AckermannDriveStamped` | Drive commands to the car |

---

## Requirements

| Requirement | Version |
|---|---|
| Ubuntu | 22.04 |
| ROS 2 | Humble |
| Python | 3.10+ |
| CUDA | 11.8+ (optional, for GPU) |
| Ultralytics | latest |
| OpenCV | 4.x |

---

## License

MIT License
