# F1tenth_PoliMI

Politecnico di Milano's [F1TENTH](https://f1tenth.org/) autonomous racing stack, developed for the ACAV course.

## Overview

F1TENTH is a 1/10-scale autonomous racing platform: a modified RC car with onboard compute and sensors that must map a track, localize itself, and race around it at high speed with no human input. This repository holds everything for our car:

- **Hardware:** parts selection, bill of materials, datasheets, CAD and wiring.
- **Software:** a ROS 2 workspace (`ros2_ws/`) with the perception, localization (SLAM), planning and control stack.
- **Documentation:** design decisions, component comparisons and notes.

> 🚧 Work in progress: the project is in the hardware selection phase. More will be added as it develops.

## Hardware

- **Compute:** NVIDIA Jetson Orin Nano Developer Kit
- **LiDAR:** under evaluation (see [LiDAR comparison](docs/hardware/LiDAR_comparison_F1TENTH.md))
- **Full parts list:** [Master BOM](hardware/bom/Master%20BOM.xlsx)

## Repository structure

```
F1tenth_PoliMI/
├── docs/                 # Documentation, design notes, reports
│   └── hardware/         # Component comparisons and hardware decisions
├── hardware/
│   ├── bom/              # Bill of materials
│   ├── datasheets/       # Component datasheets
│   ├── cad/              # 3D models, mounts, chassis plates
│   └── electronics/      # Wiring diagrams, power distribution
├── ros2_ws/              # ROS 2 colcon workspace
│   ├── src/              # ROS 2 packages
│   ├── config/           # Shared parameter files
│   └── maps/             # Track maps and racelines
└── scripts/              # Setup and utility scripts
```

## Building

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

## License

Released under the [MIT License](LICENSE).
