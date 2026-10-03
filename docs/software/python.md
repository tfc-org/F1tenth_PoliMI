# Python and IDE

All Python runs in the container: `rclpy` and the ROS packages have no host install. There is no host virtual environment.

## Container interpreter (PyCharm Professional)

`docker/ros/python3-ros` is mounted at `/opt/ros-python/bin/python`. It sources ROS and the workspace overlay, then runs `/usr/bin/python3`, so the IDE resolves `rclpy`, messages and the colcon packages.

1. `docker compose up -d arm` and `cb` once, so the workspace overlay exists.
2. Settings > Python > Interpreter > Add Interpreter > On Docker Compose, service `arm`.
3. As interpreter path enter `/opt/ros-python`. PyCharm appends `/bin/python` itself.
4. Mark each package folder in `ros2_ws/src` as Sources Root.

Afterwards:

- New packages or messages: run `cb`, then reload the interpreter paths.
- Run configurations: set Docker Compose "Command and options" to `exec` to reuse the running container.
- PyCharm leaves stopped `f1tenth_polimi-arm-run-*` containers behind. Remove them with `docker compose down --remove-orphans`, then `docker compose up -d arm`.
- `No such file or directory` on the interpreter: the bind mount is stale, see the Rebuild table in [Docker](docker.md).
