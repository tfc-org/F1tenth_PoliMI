# Simulator

f1tenth_gym + f1tenth_gym_ros for the physics, plus our `polimi_sim` package, in the `arm` / `x86` containers.

The gym alone is too kind: a perfect scan 250 times a second, commands that act instantly, a pose that is always exact. Code tuned on that breaks on the real car. `polimi_sim` puts model nodes between the gym and the stack, so the stack runs against the car's topics, frames, rates and imperfections. The gym stays the source of physics and ground truth.

## Run

One command, `simcar`, starts everything. Build the workspace once before the first run.

```bash
docker compose up -d arm
docker compose exec arm bash -c "source /etc/bashrc_polimi && cb"        # first time, and after adding files
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar"    # map spielberg, laser sl450
```

Another map:

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar levine"
```

Options go after the map:

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar levine debug_map_to_odom:=truth"   # scan drawn on the map
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar levine ideal:=true"                   # no imperfections, see Ideal mode
```

- From the host, the same in one line each: `bash scripts/sim/start.real.sh`, `start.ideal.sh`, `start.teleop.sh`, `reset.sh`, `stop.sh` (see [scripts/sim](../../scripts/sim/README.md)).
- `simcar [map] [launch args]` is a shell function from `docker/ros/bashrc_polimi`. `map` is a file name in `ros2_ws/config/maps/`. The rest goes to `ros2 launch polimi_sim sim_car.launch.py`.
- The car only moves when commanded (teleop or `/drive`).
- Stop: `Ctrl-C`.

## Configs

Each thing is defined once, in its own file under `ros2_ws/config/` (bind-mounted: no rebuild). They are chosen independently.

| File | Holds | Chosen with |
|---|---|---|
| `maps/<map>.yaml` | `map_path`, start pose `sx`, `sy`, `stheta` | `simcar <map>` |
| `lidar/<lidar>.yaml` | The laser: rate, FOV, resolution, ranges, effects | `lidar:=<lidar>` (default `sl450`) |
| `car/laser_mount.yaml` | `base_link → laser`: `x 0.27, y 0.0, z 0.11, yaw 0.0, roll 0.0` **[MEASURE]** | – |
| `sim/gym.yaml` | Everything else the gym needs: topics, vehicle preset, opponents | – |

- Maps: `spielberg` (default; Red Bull Ring, a closed track about 2.2 m wide), `levine` (a corridor loop, start at (-12, 0)).
- New map: a file with those four keys. `map_path` is absolute or relative to f1tenth_gym_ros's share directory (bundled: `maps/levine`, `maps/levine_obs`, `maps/levine_blocked`, `maps/blank`, `maps/Spielberg`). Any other `gym_bridge` parameter put there overrides `sim/gym.yaml`.
- New laser: copy `lidar/sl450.yaml`, then `simcar spielberg lidar:=<name>`.
- At launch the four files are merged into the config the gym gets, written to `/tmp/polimi_sim/gym_<map>_<lidar>.yaml`. The gym's own LiDAR takes its beam count, angles, ranges and mount from the lidar and mount files, so the laser is not described twice.
- The gym's LiDAR stays enabled, without noise, on `/sim/scan_unused`: its wall collision check runs on that scan. The stack's `/scan` comes from `lidar_model`.
- `sim/gym.yaml` is f1tenth_gym_ros's `config/sim.yaml` at the pinned commit, minus the keys above. Re-copy it when `GYM_ROS_REF` in the Dockerfile is bumped; its header lists what differs.
- Controllers must take beam angles from each `LaserScan` message (`angle_min + i * angle_increment`), never from hard-coded indices, so the same code runs with any laser and on the car.

## Graph

The gym computes where the car really is. Three model nodes turn that into what the car's sensors would report and what its actuators would do; the mux is the car's own.

```
gym_bridge ──truth pose (250 Hz)──► lidar_model ──► /scan        (frame laser, 40 Hz)
     │                        └──► odom_model  ──► /odom + TF odom→base_link (50 Hz)
     ▲ /sim/drive (100 Hz)
actuation_model ◄── /ackermann_cmd ◄── ackermann_mux ◄── /drive   (autonomy, priority 10)
                                                     ◄── /teleop  (teleop_bridge ◄── /cmd_vel, priority 100)
static TF base_link→laser  (ros2_ws/config/car/laser_mount.yaml)
truth, for evaluation only: map → ego_racecar/base_link, /ego_racecar/odom
```

Reading it bottom-up: the stack publishes `/drive`, the mux lets teleop override it, `actuation_model` delays and limits the command like the VESC and servo would, and the gym moves the car. From the new true pose, `lidar_model` produces `/scan` and `odom_model` produces `/odom`.

The stack may use only `/scan`, `/odom`, TF `odom → base_link → laser`, and publish `/drive`. It must never read `ego_racecar/*` or `/ego_racecar/odom`: those are the ground truth, which the car does not have. They are for measuring how well the stack does.

## Sim vs car

What each model changes compared with the gym alone, and what it stands for on the car:

| | Gym alone | `simcar` | Car |
|---|---|---|---|
| `/scan` | 250 Hz, all beams at one instant, frame `ego_racecar/laser` | 40 Hz, rotating-sensor timing and motion distortion, frame `laser` | SL450 driver |
| Scan errors | Gaussian noise | noise, dropouts, grazing loss, 15 m low-reflectivity limit, mixed pixels | real |
| Command path | `/drive` straight into physics, held forever | `/drive` → `ackermann_mux` (car's `mux.yaml`) → `actuation_model` | mux → VESC |
| Actuation | ideal | command delay, VESC timeout, servo delay and rate, accel / brake limits | VESC + servo |
| Odometry | ground truth in `map` | `/odom`: speed with scale error and noise, yaw rate from the commanded steering; drifts | `vesc_to_odom` |
| Frames | `map → ego_racecar/base_link → ego_racecar/laser` | `odom → base_link → laser`, truth tree kept apart | `odom → base_link → laser` |
| Teleop | `/cmd_vel` straight into physics | `/cmd_vel` → `teleop_bridge` → `/teleop` → mux | joystick → `/teleop` → mux |

## Nodes and parameters

The values are first guesses from datasheets and upstream defaults. Those marked **[MEASURE]** get replaced with measurements once the car exists, **[VERIFY]** ones need checking against the real driver or firmware.

`actuation_model`, `odom_model` and `teleop_bridge` defaults are in `ros2_ws/src/polimi_sim/config/`; the laser's are in `ros2_ws/config/lidar/`. Edits apply on the next launch. Override a whole file with a launch argument, e.g. `simcar levine odom_params:=/path/my_odom.yaml`.

### `lidar_model` (`ros2_ws/config/lidar/sl450.yaml`)

A real LiDAR spins: each beam is measured at a slightly different time, so while the car moves the scan is skewed, and some beams come back wrong or not at all. This node reproduces that. It ray-casts the gym's map with the gym's own caster, from the truth pose composed with the mount.

- Timing: `rate_hz` 40 (SL450: 15 / 20 / 25 / 30 / 40), `fov_deg` 270, `resolution_deg` 0.2 → 1351 beams, `time_increment = 1 / (rate · 1800)`, `scan_time = 1 / rate`. The sweep lasts 18.75 ms at 40 Hz.
- Motion distortion: the beams are cast in `blocks` (8) groups, each from the truth pose at that group's time. `blocks: 1` = no distortion.
- `stamp_at` (`start` | `end` of the sweep), `publish_delay` (0.002 s), `no_return_value` (`'inf'`, REP 117). **[VERIFY]** all three against the SL450 driver.
- Effects, each off at `0.0`: `noise_std` (0.01 m), `dropout_prob` (0.002), `grazing_dropout_prob` (0.5, beyond `grazing_max_deg` 80), `reflectivity_range_max` (15 m), `mixed_pixel_prob` (0.3, at jumps over `mixed_pixel_jump` 0.3 m).
- `seed` (0 = different every run).
- Cost: 0.1 ms per scan on the Mac (budget 5 ms).

### `actuation_model` (`actuation_model.yaml`)

A command does not act at once: it travels to the VESC, the servo needs time to turn, the motor cannot change speed instantly, and the VESC stops the motor when commands stop coming. This node sits where the VESC would: `/ackermann_cmd` → `/sim/drive` on a 100 Hz timer. It also publishes the steering "as sent to the VESC" on `/sim/steering_command` (`std_msgs/Float64`, rad).

- `command_delay` 0.02 s, `vesc_timeout` 0.5 s (no command for longer → speed 0; the steering stays), `steer_offset` 0.0 rad, `servo_delay` 0.03 s, `servo_rate` 3.2 rad/s, `max_steer` 0.4189 rad, `accel_max` 4.0 m/s², `brake_max` 6.0 m/s². **[MEASURE]** all of them on the car; `vesc_timeout` **[VERIFY]** in the VESC app config.
- The gym still applies its own limits afterwards (steering 3.2 rad/s, acceleration 9.51 m/s²).

### `odom_model` (`odom_model.yaml`)

The car has no GPS: it estimates its motion from the motor speed and the steering it commanded, and that estimate drifts. This node mirrors the car's `vesc_to_odom`: `/odom` (frame `odom`, child `base_link`) and TF `odom → base_link` at 50 Hz, starting from 0.

- Speed = true longitudinal speed × (1 + `speed_scale_error` 0.02) + noise `speed_noise_std` 0.02 m/s, zeroed below `speed_deadband` 0.05 m/s.
- Yaw rate = `v · tan(δ) / wheelbase`, with δ the **commanded** steering. `wheelbase` 0.3302 (gym). **[MEASURE]**: the car's `vesc.yaml` has 0.25.
- The yaw rate reads high in corners (9% at 1.5 m/s, steering 0.25 rad): the gym's tyres slip, the formula assumes they don't. `vesc_to_odom` on the car has the same error.
- `debug_map_to_odom` (`off`): publishes `map → odom`, which normally SLAM or a particle filter provides. Keep it `off` whenever one of them runs.
  - `static`: fixed at the true start pose. `/odom` and everything drawn through it (`/scan`) drift away from the map.
  - `truth`: follows the truth, like a perfect localizer. `base_link` sits on the true pose and `/scan` stays on the map. `/odom` still drifts.

### `teleop_bridge` (`teleop_bridge.yaml`)

Keyboard and Foxglove teleop speak `Twist`, the mux speaks Ackermann. This node converts, so teleop enters through the mux like the joystick does on the car: `/cmd_vel` → `/teleop`. `speed = linear.x`; steering from `angular.z`: `angular_mode: steering_angle` (rad, default) or `yaw_rate` (`atan(L·ω/v)`, `|v|` never below `min_speed`). Clamped to `max_steer`.

## Ideal mode

`simcar <map> ideal:=true`: same nodes, topics and frames, with the imperfections off. Launch it and the normal run one after the other to see what each model changes.

| Node | Overrides |
|---|---|
| `lidar_model` | `effects_enabled: false`, `blocks: 1` (no motion distortion), `publish_delay: 0.0` |
| `actuation_model` | `command_delay`, `servo_delay`, `steer_offset`: 0.0; `servo_rate`, `accel_max`, `brake_max`: 1000.0 (the gym's own limits remain) |
| `odom_model` | `speed_scale_error`, `speed_noise_std`, `speed_deadband`: 0.0 |
| `debug_map_to_odom` | `truth`, unless set on the command line |

Still there in ideal mode:

- Scan at 40 Hz with rotating-sensor time fields; `inf` for beams with no wall within 25 m.
- Mux timeout (0.2 s), VESC timeout (0.5 s), steering clamp.
- `/odom` yaw drift from tyre slip. `debug_map_to_odom: truth` keeps the drawing on the map.

The overrides are in `sim_car.launch.py` (`IDEAL_*`). They win over the parameter files.

## Change parameters while running

Useful to feel what one imperfection does: change it, watch the stack react, no relaunch.

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && ros2 param set /lidar_model noise_std 0.0"
docker compose exec arm bash -c "source /etc/bashrc_polimi && ros2 param set /actuation_model servo_delay 0.05"
```

Live: all `lidar_model` effects, all `actuation_model` and `teleop_bridge` values, the `odom_model` error values. Fixed at start: rates, scan geometry, `range_max`, topics, frames.

Ideal scan, to compare with the gym's (`/sim/scan_unused`, noise-free):

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && ros2 param set /lidar_model effects_enabled false"
```

- Car standing still: the two scans match, except a few beams (the gym rounds beam angles to a table, so a block can start one entry later).
- Car moving: they differ by the motion distortion. Set `blocks: 1` in the lidar file to remove it.

## Foxglove

### Connect

- Browser: https://app.foxglove.dev (free account) or the desktop app.
- **Open connection → Foxglove WebSocket →** `ws://localhost:8765`.
- Ready-made layout, then **Layouts → Import from file**:
  ```bash
  docker cp f1tenth_polimi_arm:/opt/sim_ws/src/f1tenth_gym_ros/config/foxglove/gym_bridge_foxglove.json ~/Desktop/
  ```
  The layout predates `simcar`: its scan entry points at the gym's scan, so enable `/scan` by hand.

### Truth and estimate

There are two frame trees, and by default nothing connects them: `map → ego_racecar/base_link` (where the car really is) and `odom → base_link → laser` (where the car thinks it is). On the real car, SLAM or localization provides the missing `map → odom`. Until the stack has one, `debug_map_to_odom` fakes it.

- Display frame `map`: `ego_racecar/base_link` is the truth.
- `/scan` is in frame `laser`: it shows only when `laser` connects to the display frame. Display frame `odom` or `base_link`, or a `debug_map_to_odom` mode.
- `debug_map_to_odom:=truth`: scan on the map. Use it to look at the scan.
- `debug_map_to_odom:=static`: the scan and `base_link` rotate away from the map as the odometry drifts, about 8° per 90° corner. Use it to look at the drift.
- A wall hit makes the truth jump: the gym zeroes the car's heading on collision. `/odom` does not follow.

### Messages you will see

- `N Infinity invalid values detected`: harmless. Those are the beams with no return (`inf`, REP 117); Foxglove cannot colour them by distance. Set the scan's colour mode to flat to silence it.
- `Missing transform from frame <laser> to frame <...>`: the display frame is in the truth tree and nothing links `map` to `odom`. Launch with `debug_map_to_odom:=truth`, or set the display frame to `base_link`.

## Drive (teleop)

Teleop goes through the mux, exactly like the joystick on the car. Use the Foxglove **Teleop** panel on `/cmd_vel` (up / down as `linear-x`, left / right as `angular-z`, which is the steering angle in rad), or the keyboard in a second shell:

```bash
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && ros2 run teleop_twist_keyboard teleop_twist_keyboard"
```

- Teleop has priority 100, autonomy (`/drive`) 10. While teleop messages arrive, they win.
- The mux input times out after 0.2 s: **hold** the key or the panel button. One key press does not keep driving until `k`, as it does with the gym alone.
- Let go: autonomy takes over again. With no autonomy the car stops 0.5 s later (VESC timeout).
- Keyboard: keys work only while that terminal has focus. No arrow keys (they send zeros).
- `i` forward · `,` reverse · `k` stop · `u` / `o` forward-left / forward-right. `q` / `z`: speed ±10% (starts at 0.5 m/s).
- Keyboard `angular.z` is 1.0, so `u` / `o` give full lock (clamped to 0.4189 rad).

## Reset position

Puts the car back on the track after a crash or to start again from a known place.

Stop the car first: a reset keeps the last speed. Then:

Foxglove 3D panel → publish tool → **Pose estimate** → click and drag; or
```bash
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped '{header: {frame_id: map}, pose: {pose: {position: {x: -12.0, y: 0.0}, orientation: {w: 1.0}}}}'"
```

The command above is the `levine` start. For `spielberg` use `position: {x: 0.0, y: 0.0}, orientation: {z: 0.1296, w: 0.9916}`.

After a crash the car stays stuck until reset.

Both of these move only the true car. To also start `/odom` again from 0, use `bash scripts/sim/reset.sh` from the host, or add:
```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && ros2 service call /odom_model/reset std_srvs/srv/Empty"
```

## Topics

The first three are all the stack touches, on the simulator and on the car alike. The rest is for driving by hand, resetting, and evaluation.

| Topic | Type | |
|---|---|---|
| `/scan` | `sensor_msgs/LaserScan`, frame `laser`, 40 Hz | out, `lidar_model` |
| `/odom` | `nav_msgs/Odometry`, frame `odom`, 50 Hz | out, `odom_model` |
| `/drive` | `ackermann_msgs/AckermannDriveStamped` | in (autonomy, mux priority 10) |
| `/teleop` | `ackermann_msgs/AckermannDriveStamped` | in (mux priority 100), from `teleop_bridge` |
| `/cmd_vel` | `geometry_msgs/Twist` | in (teleop) |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | in (reset) |
| `/map` | `nav_msgs/OccupancyGrid` | out |
| `/ego_racecar/odom` | `nav_msgs/Odometry`, ground truth in `map` | out, evaluation only |
| `/ego_racecar/collision` | `std_msgs/Bool` | out, evaluation only |
| `/ackermann_cmd`, `/sim/drive`, `/sim/steering_command`, `/sim/scan_unused` | internal | – |

## RViz (optional, via noVNC)

```bash
docker compose --profile gui up -d novnc          # on the host
rviz2 -d /opt/sim_ws/src/f1tenth_gym_ros/config/rviz/gym_bridge.rviz   # in the container
```

- View at http://localhost:8080.
- Software rendering breaks the **Map** display (GLSL error): untick it; scan and car still draw.

## Tests

The model logic is plain Python without ROS, unit-tested on synthetic data:

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && cd ~/ws/src/polimi_sim && python3 -m pytest test -q"
```

## The gym alone

No model nodes, no mux, upstream config (ideal 250 Hz scan, `ego_racecar/*` frames, SICK TIM571 LiDAR). Only for checking whether a problem is in the gym or in `polimi_sim`:

```bash
docker compose exec arm bash \
  -c "source /etc/bashrc_polimi && ros2 launch f1tenth_gym_ros gym_bridge_launch.py open_foxglove:=false"
```

## Known limits

Where the simulator still differs from the car, or simplifies:

- No camera, and no room with a taped track: the maps are tracks bounded by walls, which the [scope](../scope.md) no longer has. The LiDAR sees those walls; in the room it will see only the room.
- Truth pose: the gym's single-track state is at the centre of gravity, and the bridge publishes it as `ego_racecar/base_link`. `polimi_sim` treats it as `base_link` (rear axle on the car): a 0.17 m offset.
- Vehicle body parameters are the gym's `f1tenth` preset.
- The truth pose changes at 100 Hz (physics step). `lidar_model` interpolates between steps and extrapolates up to 30 ms past the newest one.
- Grazing loss and mixed pixels are computed from neighbouring beams, not from the map geometry.
- `lidar_model` needs the bridge on wall-clock time: `use_sim_time: False` in `sim/gym.yaml`.
- The gym's 3D car model and wheels stay on the `ego_racecar/*` frames.
- `/initialpose` alone moves the truth, not `/odom`: wheel odometry keeps integrating, as on the car. `scripts/sim/reset.sh` also calls `/odom_model/reset`, which zeroes `/odom` and re-pins the `debug_map_to_odom:=static` overlay.

## Troubleshooting

- `ros2 topic list` shows only `/rosout`, `/parameter_events`: zenoh router down. `docker compose restart arm`.
- `/cmd_vel` all zeros: wrong window focused or arrow keys.
- Foxglove can't connect: sim not running, or container started before this compose change (`docker compose up -d --force-recreate arm`).
- `simcar: command not found` or `/etc/bashrc_polimi: No such file or directory`: `docker compose restart arm` (see [docker.md](docker.md)).
- `Package 'polimi_sim' not found`: build it, `cb`.
