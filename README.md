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
├── docs/                 # Documentation, design notes, reports
│   └── hardware/         # Component comparisons and hardware decisions
├── hardware/
│   ├── bom/              # Bill of materials
│   ├── datasheets/       # Component datasheets
│   ├── cad/              # 3D models, mounts, chassis plates
│   └── electronics/      # Wiring diagrams, power distribution
├── docker/
│   ├── ros/              # Dev / car image (ros:humble + deps + simulator)
│   └── novnc/            # Virtual display + browser viewer for RViz
├── docker-compose.yaml   # Services: arm (Apple Silicon), x86 (PC), jet (Orin Nano), novnc
├── ros2_ws/              # ROS 2 colcon workspace
│   ├── src/
│   │   ├── f1tenth_system/   # Submodule: our fork of f1tenth/f1tenth_system (drivers)
│   │   └── polimi_*/         # Our own ROS 2 packages
│   ├── config/           # Shared parameter files
│   └── maps/             # Track maps and racelines
└── scripts/              # Setup and utility scripts
```

## Software stack

| Component | Source | How it gets here |
|---|---|---|
| Drivers: VESC, ackermann_mux, joystick teleop | [f1tenth/f1tenth_system](https://github.com/f1tenth/f1tenth_system) `humble-devel` | Submodule at `ros2_ws/src/f1tenth_system`, tracking our fork's `humble-polimi` branch |
| Simulator | [f1tenth/f1tenth_gym](https://github.com/f1tenth/f1tenth_gym) `dev-humble` | pip-installed in the arm / x86 image at a pinned commit (`GYM_REF` in `docker/ros/Dockerfile`) |
| Simulator ROS bridge | [f1tenth/f1tenth_gym_ros](https://github.com/f1tenth/f1tenth_gym_ros) `dev-humble` | Built in the arm / x86 image under `/opt/sim_ws` at a pinned commit (`GYM_ROS_REF`) |

The simulator is not installed on the car (`jet`). Bump `GYM_REF` / `GYM_ROS_REF` on purpose and rebuild the image; never follow the branch.

Rule of thumb: new functionality goes in a new `polimi_*` package in this repo; only fixes we can't make from outside go into the f1tenth_system fork.

## Getting started

Clone with submodules, then run the one-time git setup:

```bash
git clone --recurse-submodules https://github.com/tfc-org/F1tenth_PoliMI.git
cd F1tenth_PoliMI
bash scripts/setup_git.sh
```

`setup_git.sh` fetches all submodules (f1tenth_system has its own: vesc, ackermann_mux, teleop_tools) and sets three local git options that git does not copy on clone:

- `push.recurseSubmodules check`: refuses to push this repo if it points at a submodule commit that is not on GitHub yet.
- `submodule.recurse true`: `git pull` and `git switch` also move submodules to the right commit.
- an `upstream` remote in each fork, pointing at the original repo.

## Docker

```bash
cp .env.example .env              # once: set HOST_UID / HOST_GID (id -u / id -g)
docker compose build arm          # arm = Apple Silicon, x86 = PC, jet = Orin Nano
docker compose up -d arm          # also starts novnc
docker compose exec arm bash
cb                                # colcon build + source
```

Simulator (arm / x86):

```bash
ros2 launch f1tenth_gym_ros gym_bridge_launch.py open_foxglove:=false
```

View it in [Foxglove](https://app.foxglove.dev) at `ws://localhost:8765`, or RViz in the browser at http://localhost:8080 (noVNC). Rebuild the image whenever a `package.xml` changes: rosdep runs at build time.

## Working with the f1tenth_system submodule

The submodule is a full clone of our fork: edit, commit and push inside it. This repo only stores *which commit* of the fork to use, so every change to the fork takes two commits.

```bash
cd ros2_ws/src/f1tenth_system
git switch humble-polimi             # submodules start in detached HEAD
# edit, build, test
git add -A && git commit -m "..."
git push                             # 1) pushes to the fork

cd ../../..
git add ros2_ws/src/f1tenth_system
git commit -m "Bump f1tenth_system: ..."
git push                             # 2) pushes the new pointer
```

Syncing with upstream:

```bash
cd ros2_ws/src/f1tenth_system
git fetch upstream
git log --oneline humble-polimi..upstream/humble-devel   # what's new upstream
git switch humble-polimi && git merge upstream/humble-devel
git submodule update --init --recursive                  # nested submodules may have moved
git push
```

Then bump the pointer in this repo as above.

## Building

Inside the container:

```bash
cd ~/ws
colcon build --symlink-install
source install/setup.bash
```

## License

Released under the [MIT License](LICENSE).
