# F1tenth_PoliMI

Politecnico di Milano's [F1TENTH](https://f1tenth.org/) autonomous racing stack, developed for the ACAV course.

## Overview

F1TENTH is a 1/10-scale autonomous racing platform: a modified RC car with onboard compute and sensors that must map a track, localize itself, and race around it at high speed with no human input. This repository holds everything for our car:

- **Hardware:** parts selection, bill of materials, datasheets, CAD and wiring.
- **Software:** a ROS 2 workspace (`ros2_ws/`) with the perception, localization (SLAM), planning and control stack, and a simulator that behaves like the car so the stack can be written before the car exists.
- **Documentation:** design decisions, component comparisons and notes.

Our course setup is not a standard F1TENTH track: the car races in a room on a track drawn with tape on the floor. See [Project scope](docs/scope.md).

> 🚧 Work in progress: the hardware is still being selected and the car is not built. Meanwhile the software is developed against the simulator.

## Hardware

- **Compute:** NVIDIA Jetson Orin Nano Developer Kit
- **LiDAR:** Orbbec Pulsar SL450 (see [LiDAR comparison](docs/hardware/LiDAR_comparison_F1TENTH.md))
- **Camera:** Orbbec Gemini 335L (see [camera comparison](docs/hardware/Camera_comparison_F1TENTH.md))
- **Chassis:** Traxxas Ford Fiesta ST Rally VXL (74276-4); see [chassis sourcing](docs/hardware/Fiesta_ST_Rally_VXL_sourcing_F1TENTH.md)
- **Full parts list:** [Master BOM](hardware/bom/master_bom.xlsx)

## Repository structure

```
F1tenth_PoliMI/
├── docs/
│   ├── scope.md          # What the car must do, and where
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
│   ├── config/               # maps, lidar, car, sim: one file per thing, no rebuild
│   └── maps/                 # Our own map images (none yet)
└── scripts/              # setup_git.sh, sim/ (start, teleop, reset, stop the simulator)
```

## Quick start (simulator)

Everything runs in Docker; nothing is installed on the host besides Docker itself.

```bash
git clone --recurse-submodules https://github.com/tfc-org/F1tenth_PoliMI.git
cd F1tenth_PoliMI && bash scripts/setup_git.sh
cp .env.example .env              # set HOST_UID / HOST_GID
docker compose build arm          # x86 on a PC
docker compose up -d arm
docker compose exec arm bash
cb                                # build the workspace (first time)
simcar                            # simulator as the car: map spielberg, laser sl450
```

Once the image is built, `bash scripts/sim/start.real.sh` does the last four lines in one go.

Then open Foxglove at `ws://localhost:8765` to see the track, the car and the scan. The car stands still until it gets a command: [Simulator](docs/software/simulator.md) shows how to drive it.

## Documentation

New here: read Setup, then Simulator. The others are references for when you need them.

| Doc | Contents |
|---|---|
| [Project scope](docs/scope.md) | Environment (room, taped track) and what the car must do |
| [Setup](docs/software/setup.md) | Stack, clone, git config, `.env`, first build |
| [Docker](docs/software/docker.md) | Services, networking, day-to-day commands, cleanup |
| [Python and IDE](docs/software/python.md) | PyCharm interpreter in the container |
| [Simulator](docs/software/simulator.md) | `simcar`: run, map / laser configs, model nodes and parameters, Foxglove, teleop, reset, topics |
| [Git and submodules](docs/software/git.md) | Editing and syncing the f1tenth_system fork |
| [Car](docs/software/car.md) | Bringup and to-dos (car not here yet) |
| [LiDAR comparison](docs/hardware/LiDAR_comparison_F1TENTH.md) | Candidate LiDARs and pick |
| [Camera comparison](docs/hardware/Camera_comparison_F1TENTH.md) | Candidate cameras and pick |
| [Chassis sourcing](docs/hardware/Fiesta_ST_Rally_VXL_sourcing_F1TENTH.md) | Fiesta ST Rally VXL and parts |

## License

Released under the [MIT License](LICENSE).
