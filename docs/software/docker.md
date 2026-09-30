# Docker

## Services

| Service | Use | Simulator | Networking |
|---|---|---|---|
| `arm` | Apple Silicon Mac | yes | ports: `8765` (Foxglove) |
| `x86` | Linux / Windows PC | yes | ports: `8765` (Foxglove) |
| `jet` | Orin Nano on the car | no | host |
| `novnc` | Optional browser display for RViz (profile `gui`) | – | port `8080` |

- One image per target, built from `docker/ros/Dockerfile` on `ros:humble`.
- Bind mounts: `ros2_ws/src`, `ros2_ws/config`, `ros2_ws/maps`.
- `build/`, `install/`, `log/` live in Docker volumes (`build_arm`, …), not in the repo.
- Ports bind to `127.0.0.1` only.

## Docker Desktop from the command line (macOS)

```bash
docker desktop start              # or: open -a Docker
docker desktop status
docker desktop restart
docker desktop stop
```

No Docker Desktop settings are needed for this repo.

## Everyday commands

```bash
docker compose up -d arm                   # start
docker compose exec arm bash               # shell (repeat per terminal)
docker compose ps                          # what is running
docker compose logs -f arm                 # container output
docker compose exec arm cat /tmp/zenohd.log   # zenoh router log
docker compose restart arm                 # restart (e.g. zenoh router died)
docker compose down                        # stop and remove containers
```

Inside the container:

```bash
cb                                         # colcon build --symlink-install + source
sauce                                      # re-source ROS + workspace
```

## Rebuild

```bash
docker compose build arm                   # after package.xml / GYM_REF changes
docker compose build --no-cache arm        # from scratch
docker compose up -d --force-recreate arm  # use the new image
```

## Optional noVNC (RViz)

```bash
docker compose --profile gui up -d novnc   # then http://localhost:8080
docker compose rm -sf novnc                # stop and remove
```

## Cleanup

```bash
docker compose down -v                     # also delete build/install/log volumes
docker system df                           # disk usage
docker image prune                         # dangling images
docker builder prune                       # build cache
```
