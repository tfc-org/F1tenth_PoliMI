# Simulator

f1tenth_gym + f1tenth_gym_ros, in the `arm` / `x86` containers.

Two modes:

- **`simcar`** ([sim_car.md](sim_car.md)): the normal one. The gym plus `polimi_sim`, so the stack sees the car's topics, frames, rates and imperfections.
- **`sim`** (this page): the raw gym. Ideal 250 Hz scan, no mux, `ego_racecar/*` frames. For checking the gym itself.

## Run

```bash
docker compose up -d arm
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && source /etc/bashrc_polimi && sim" # = our ros2_ws/config/sim/sim_sl450.yaml
```

- `sim` is a shell function from `docker/ros/bashrc_polimi`, which is bind-mounted: after a change, just open a new shell. Containers created before the mount was added need `docker compose up -d arm` once.
- `sim <name>` loads `ros2_ws/config/sim/<name>.yaml`. `sim sim.yaml` runs the upstream config shipped with f1tenth_gym_ros. Anything after the name goes to `ros2 launch`, e.g. `sim sim_sl450 num_agent:=2`.
- Without the function: `ros2 launch f1tenth_gym_ros gym_bridge_launch.py open_foxglove:=false config:=$HOME/ws/config/sim/sim_sl450.yaml`.
- Default map `levine`, car starts at (-12, 0).
- The car only moves when commanded (keyboard or `/drive`).
- Stop: `Ctrl-C`.

## Sim configs

`ros2_ws/config/sim/` holds our copies of f1tenth_gym_ros's `config/sim.yaml`. The bridge reads the whole file, so each copy is complete. Re-copy them when `GYM_ROS_REF` in the Dockerfile is bumped.

| Config | LiDAR | Notes |
|---|---|---|
| `sim_sl450.yaml` (default) | 1351 beams, ±135°, 0.2°, noise σ 2 cm | Mimics the Orbbec Pulsar SL450. Mount `[0.275, 0, 0]` is still the upstream default (TODO: measure). |
| `sim.yaml` (upstream) | 819 beams, ±135°, ≈0.33°, noise σ 1 cm | SICK TIM571 defaults. |

- Beam spacing in f1tenth_gym is `(angle_max - angle_min) / (num_beams - 1)`. The comment in upstream `sim.yaml` says `/ num_beams`, which is wrong.
- The sim publishes `/scan` far faster than a real LiDAR (topic timer 4 ms in async mode), while the SL450 tops out at 40 Hz. Don't tune timing-sensitive logic on sim scan rate alone.
- `open_foxglove` / `target` in our copies are ignored: the launch file reads those defaults from the package's own `sim.yaml`.
- Controllers must take beam angles from each `LaserScan` message (`angle_min + i * angle_increment`), never from hard-coded indices, so the same code runs on both configs and on the car.

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
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && ros2 run teleop_twist_keyboard teleop_twist_keyboard"
```

- Keys work only while that terminal has focus. No arrow keys (they send zeros).
- `i` forward · `,` reverse · `k` stop · `u` / `o` forward-left / forward-right.
- `q` / `z`: speed ±10% (starts at 0.5 m/s).
- The last command holds: one `i` drives until `k`.
- Steering is fixed at ±0.3 rad (gym_bridge keyboard mapping).

## Reset position

Press `k` first: a reset keeps the last speed. Then:

Foxglove 3D panel → publish tool → **Pose estimate** → click and drag; or
```bash
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped '{header: {frame_id: map}, pose: {pose: {position: {x: -12.0, y: 0.0}, orientation: {w: 1.0}}}}'"
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
