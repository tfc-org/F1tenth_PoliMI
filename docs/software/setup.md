# Setup

## Stack

- **Drivers:** [f1tenth_system](https://github.com/f1tenth/f1tenth_system) `humble-devel` (VESC, ackermann_mux, joystick teleop). Submodule at `ros2_ws/src/f1tenth_system`, our fork's `humble-polimi` branch.
- **Simulator:** [f1tenth_gym](https://github.com/f1tenth/f1tenth_gym) + [f1tenth_gym_ros](https://github.com/f1tenth/f1tenth_gym_ros) `dev-humble`, pinned by `GYM_REF` / `GYM_ROS_REF` in `docker/ros/Dockerfile`. In the `arm` / `x86` images only.
- **Our code:** `polimi_*` packages in `ros2_ws/src`. Only fixes we can't make from outside go into the fork.
- **Middleware:** ROS 2 Humble, `rmw_zenoh_cpp`. The zenoh router starts with the container.

## First time

```bash
git clone --recurse-submodules https://github.com/tfc-org/F1tenth_PoliMI.git
cd F1tenth_PoliMI
bash scripts/setup_git.sh
cp .env.example .env
id -u; id -g                      # put these in .env as HOST_UID / HOST_GID
docker compose build arm          # arm = Apple Silicon, x86 = PC, jet = Orin Nano
```

- `setup_git.sh` fetches submodules and sets `push.recurseSubmodules=check`, `submodule.recurse=true` and an `upstream` remote in the fork. Safe to re-run.
- First build takes a while (gym + gym_ros).

## Rebuild the image when

- the `Dockerfile` changes;
- a `package.xml` changes (rosdep runs at build time);
- `GYM_REF` / `GYM_ROS_REF` is bumped. Bump on purpose, never follow the branch.
