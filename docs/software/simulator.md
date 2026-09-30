# Simulator

f1tenth_gym + f1tenth_gym_ros, in the `arm` / `x86` containers.

## Run

```bash
docker compose up -d arm
docker compose exec arm bash
ros2 launch f1tenth_gym_ros gym_bridge_launch.py open_foxglove:=false
```

- Default map `levine`, car starts at (-12, 0).
- The car only moves when commanded (keyboard or `/drive`).
- Stop: `Ctrl-C`.

## Foxglove

- Browser: https://app.foxglove.dev (free account) or the desktop app.
- **Open connection → Foxglove WebSocket →** `ws://localhost:8765`.
- Ready-made layout, then **Layouts → Import from file**:
  ```bash
  docker cp f1tenth_polimi_arm:/opt/sim_ws/src/f1tenth_gym_ros/config/foxglove/gym_bridge_foxglove.json ~/Desktop/
  ```

## Drive (keyboard)

Second container shell:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

- Keys work only while that terminal has focus. No arrow keys (they send zeros).
- `i` forward · `,` reverse · `k` stop · `u` / `o` forward-left / forward-right.
- `q` / `z`: speed ±10% (starts at 0.5 m/s).
- The last command holds: one `i` drives until `k`.
- Steering is fixed at ±0.3 rad (gym_bridge keyboard mapping).

## Reset position

Press `k` first: a reset keeps the last speed. Then:

- Foxglove 3D panel → publish tool → **Pose estimate** → click and drag; or
- ```bash
  ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
    "{header: {frame_id: map}, pose: {pose: {position: {x: -12.0, y: 0.0}, orientation: {w: 1.0}}}}"
  ```

After a crash the car stays stuck until reset.

## Topics

| Topic | Type | |
|---|---|---|
| `/scan` | `sensor_msgs/LaserScan` | out |
| `/ego_racecar/odom` | `nav_msgs/Odometry`, ground truth in `map` | out |
| `/map` | `nav_msgs/OccupancyGrid` | out |
| `/ego_racecar/collision` | `std_msgs/Bool` | out |
| `/drive` | `ackermann_msgs/AckermannDriveStamped` | in (autonomy) |
| `/cmd_vel` | `geometry_msgs/Twist` | in (keyboard) |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | in (reset) |

## RViz (optional, via noVNC)

```bash
docker compose --profile gui up -d novnc          # on the host
rviz2 -d /opt/sim_ws/src/f1tenth_gym_ros/config/rviz/gym_bridge.rviz   # in the container
```

- View at http://localhost:8080.
- Software rendering breaks the **Map** display (GLSL error): untick it; scan and car still draw.

## Troubleshooting

- `ros2 topic list` shows only `/rosout`, `/parameter_events`: zenoh router down. `docker compose restart arm`.
- `/cmd_vel` all zeros: wrong window focused or arrow keys.
- Foxglove can't connect: sim not running, or container started before this compose change (`docker compose up -d --force-recreate arm`).
