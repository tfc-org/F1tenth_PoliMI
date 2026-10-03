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
- **Chassis:** Traxxas Ford Fiesta ST Rally VXL (74276-4); see [chassis sourcing](docs/hardware/Fiesta_ST_Rally_VXL_sourcing_F1TENTH.md)
- **Full parts list:** [Master BOM](hardware/bom/master_bom.xlsx)

## Repository structure

```
F1tenth_PoliMI/
├── docs/
│   ├── hardware/         # Component comparisons and hardware decisions
│   └── software/         # Setup, Docker, Python/IDE, simulator, git, car
├── hardware/             # BOM, datasheets, CAD, electronics
├── docker/
│   ├── ros/              # ROS image (ros:humble + deps + simulator)
│   └── novnc/            # Optional browser display for RViz
├── docker-compose.yaml   # Services: arm, x86, jet, novnc
├── ros2_ws/
│   ├── src/
│   │   ├── f1tenth_system/   # Submodule: drivers (our fork)
│   │   └── polimi_*/         # Our packages
│   ├── config/
│   └── maps/
└── scripts/              # setup_git.sh
```

## Quick start (simulator)

```bash
git clone --recurse-submodules https://github.com/tfc-org/F1tenth_PoliMI.git
cd F1tenth_PoliMI && bash scripts/setup_git.sh
cp .env.example .env              # set HOST_UID / HOST_GID
docker compose build arm          # x86 on a PC
docker compose up -d arm
docker compose exec arm bash
sim                               # simulator with ros2_ws/config/sim/sim_sl450.yaml
```

Then open Foxglove at `ws://localhost:8765`.

## Documentation

| Doc | Contents |
|---|---|
| [Setup](docs/software/setup.md) | Stack, clone, git config, `.env`, first build |
| [Docker](docs/software/docker.md) | Services, networking, day-to-day commands, cleanup |
| [Python and IDE](docs/software/python.md) | PyCharm interpreter in the container |
| [Simulator](docs/software/simulator.md) | Run, sim configs, Foxglove, drive, reset, topics, RViz |
| [Git and submodules](docs/software/git.md) | Editing and syncing the f1tenth_system fork |
| [Car](docs/software/car.md) | Bringup and to-dos (car not here yet) |
| [LiDAR comparison](docs/hardware/LiDAR_comparison_F1TENTH.md) | Candidate LiDARs and pick |
| [Chassis sourcing](docs/hardware/Fiesta_ST_Rally_VXL_sourcing_F1TENTH.md) | Fiesta ST Rally VXL and parts |

## License

Released under the [MIT License](LICENSE).
