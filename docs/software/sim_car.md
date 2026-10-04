# Simulator as the car (`simcar`)

`polimi_sim` puts model nodes between the gym and the stack, so the stack runs against the car's topics, frames, rates and imperfections. The gym stays the source of physics and ground truth.

## Run

```bash
docker compose up -d arm
docker compose exec arm bash -c "source /etc/bashrc_polimi && cb"        # first time, and after adding files
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar"    # levine
```

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar spielberg"
docker compose exec arm bash -c "source /etc/bashrc_polimi && simcar spielberg debug_map_to_odom:=truth"   # scan drawn on the map
```

- `simcar [map] [launch args]`: `map` is a file name in `ros2_ws/config/sim/` (`levine`, `spielberg`). The rest goes to `ros2 launch polimi_sim sim_car.launch.py`.
- Foxglove: `ws://localhost:8765`, as in [simulator.md](simulator.md).
- Stop: `Ctrl-C`.

## Graph

```
gym_bridge ──truth pose (250 Hz)──► lidar_model ──► /scan        (frame laser, 40 Hz)
     │                        └──► odom_model  ──► /odom + TF odom→base_link (50 Hz)
     ▲ /sim/drive (100 Hz)
actuation_model ◄── /ackermann_cmd ◄── ackermann_mux ◄── /drive   (autonomy, priority 10)
                                                     ◄── /teleop  (teleop_bridge ◄── /cmd_vel, priority 100)
static TF base_link→laser  (ros2_ws/config/car/laser_mount.yaml)
truth, for evaluation only: map → ego_racecar/base_link, /ego_racecar/odom
```

The stack may use only `/scan`, `/odom`, TF `odom → base_link → laser`, and publish `/drive`. It must never read `ego_racecar/*` or `/ego_racecar/odom`.

## Sim vs car

| | Raw gym (`sim`) | `simcar` | Car |
|---|---|---|---|
| `/scan` | 250 Hz, all beams at one instant, frame `ego_racecar/laser` | 40 Hz, rotating-sensor timing and motion distortion, frame `laser` | SL450 driver |
| Scan errors | Gaussian noise | noise, dropouts, grazing loss, 15 m low-reflectivity limit, mixed pixels | real |
| Command path | `/drive` straight into physics, held forever | `/drive` → `ackermann_mux` (car's `mux.yaml`) → `actuation_model` | mux → VESC |
| Actuation | ideal | command delay, VESC timeout, servo delay and rate, accel / brake limits | VESC + servo |
| Odometry | ground truth in `map` | `/odom`: speed with scale error and noise, yaw rate from the commanded steering; drifts | `vesc_to_odom` |
| Frames | `map → ego_racecar/base_link → ego_racecar/laser` | `odom → base_link → laser`, truth tree kept apart | `odom → base_link → laser` |
| Teleop | `/cmd_vel` straight into physics | `/cmd_vel` → `teleop_bridge` → `/teleop` → mux | joystick → `/teleop` → mux |

## Nodes and parameters

Defaults in `ros2_ws/src/polimi_sim/config/`. The build uses `--symlink-install`: edits apply on the next launch. Override a whole file with a launch argument, e.g. `simcar levine lidar_params:=/path/my_lidar.yaml`.

### `lidar_model` (`lidar_model.yaml`)

Ray-casts the gym's map with the gym's own caster, from the truth pose composed with the mount.

- Timing: `rate_hz` 40 (SL450: 15 / 20 / 25 / 30 / 40), `fov_deg` 270, `resolution_deg` 0.2 → 1351 beams, `time_increment = 1 / (rate · 1800)`, `scan_time = 1 / rate`. The sweep lasts 18.75 ms at 40 Hz.
- Motion distortion: the beams are cast in `blocks` (8) groups, each from the truth pose at that group's time. `blocks: 1` = no distortion.
- `stamp_at` (`start` | `end` of the sweep), `publish_delay` (0.002 s), `no_return_value` (`'inf'`, REP 117). **[VERIFY]** all three against the SL450 driver.
- Effects, each off at `0.0`: `noise_std` (0.01 m), `dropout_prob` (0.002), `grazing_dropout_prob` (0.5, beyond `grazing_max_deg` 80), `reflectivity_range_max` (15 m), `mixed_pixel_prob` (0.3, at jumps over `mixed_pixel_jump` 0.3 m).
- `seed` (0 = different every run).
- Cost: 0.1 ms per scan on the Mac (budget 5 ms).

### `actuation_model` (`actuation_model.yaml`)

`/ackermann_cmd` → `/sim/drive` on a 100 Hz timer. Also publishes the steering "as sent to the VESC" on `/sim/steering_command` (`std_msgs/Float64`, rad).

- `command_delay` 0.02 s, `vesc_timeout` 0.5 s (no command for longer → speed 0; the steering stays), `steer_offset` 0.0 rad, `servo_delay` 0.03 s, `servo_rate` 3.2 rad/s, `max_steer` 0.4189 rad, `accel_max` 4.0 m/s², `brake_max` 6.0 m/s². **[MEASURE]** all of them on the car; `vesc_timeout` **[VERIFY]** in the VESC app config.
- The gym still applies its own limits afterwards (steering 3.2 rad/s, acceleration 9.51 m/s²).

### `odom_model` (`odom_model.yaml`)

Mirrors `vesc_to_odom`: `/odom` (frame `odom`, child `base_link`) and TF `odom → base_link` at 50 Hz, starting from 0.

- Speed = true longitudinal speed × (1 + `speed_scale_error` 0.02) + noise `speed_noise_std` 0.02 m/s, zeroed below `speed_deadband` 0.05 m/s.
- Yaw rate = `v · tan(δ) / wheelbase`, with δ the **commanded** steering. `wheelbase` 0.3302 (gym). **[MEASURE]**: the car's `vesc.yaml` has 0.25.
- The yaw rate reads high in corners (9% at 1.5 m/s, steering 0.25 rad): the gym's tyres slip, the formula assumes they don't. `vesc_to_odom` on the car has the same error.
- `debug_map_to_odom` (`off`): publishes `map → odom`, which normally SLAM or a particle filter provides. Keep it `off` whenever one of them runs.
  - `static`: fixed at the true start pose. `/odom` and everything drawn through it (`/scan`) drift away from the map.
  - `truth`: follows the truth, like a perfect localizer. `base_link` sits on the true pose and `/scan` stays on the map. `/odom` still drifts.

### `teleop_bridge` (`teleop_bridge.yaml`)

`/cmd_vel` → `/teleop`. `speed = linear.x`; steering from `angular.z`: `angular_mode: steering_angle` (rad, default) or `yaw_rate` (`atan(L·ω/v)`, `|v|` never below `min_speed`). Clamped to `max_steer`.

### Shared files

- `ros2_ws/config/car/laser_mount.yaml`: `base_link → laser`, `x 0.27, y 0.0, z 0.11, yaw 0.0, roll 0.0` **[MEASURE]**. Read by the launch for the static TF and for `lidar_model`. Keep `lidar_base_link_to_lidar_tf` in the gym configs equal to it.
- `ros2_ws/config/sim/levine.yaml`, `spielberg.yaml`: gym configs in car mode. The header of each file lists the differences from upstream. The gym's own LiDAR stays enabled on `/sim/scan_unused`: its wall collision check runs on that scan.

## Change parameters while running

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
- Car moving: they differ by the motion distortion. Launch with a copy of `lidar_model.yaml` with `blocks: 1` to remove it.

## Teleop

Foxglove **Teleop** panel on `/cmd_vel`, or:

```bash
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && ros2 run teleop_twist_keyboard teleop_twist_keyboard"
```

- Teleop has priority 100, autonomy (`/drive`) 10. While teleop messages arrive, they win.
- The mux input times out after 0.2 s: **hold** the key or the panel button. One key press no longer drives until `k`, as it does in the raw gym.
- Let go: autonomy takes over again. With no autonomy the car stops 0.5 s later (VESC timeout).

## Truth vs estimate in Foxglove

- Display frame `map`: `ego_racecar/base_link` is the truth.
- `base_link` belongs to the `odom` tree, which nothing ties to `map` until SLAM or localization runs.
- `/scan` is in frame `laser`: it shows only when `laser` connects to the display frame. Display frame `odom` or `base_link`, or a `debug_map_to_odom` mode.
- `debug_map_to_odom:=truth`: scan on the map. Use it to look at the scan.
- `debug_map_to_odom:=static`: the scan and `base_link` rotate away from the map as the odometry drifts, about 8° per 90° corner. Use it to look at the drift.
- A wall hit makes the truth jump: the gym zeroes the car's heading on collision. `/odom` does not follow.

## Tests

```bash
docker compose exec arm bash -c "source /etc/bashrc_polimi && cd ~/ws/src/polimi_sim && python3 -m pytest test -q"
```

## Known limits

- Truth pose: the gym's single-track state is at the centre of gravity, and the bridge publishes it as `ego_racecar/base_link`. `polimi_sim` treats it as `base_link` (rear axle on the car): a 0.17 m offset.
- Vehicle body parameters are the gym's `f1tenth` preset.
- The truth pose changes at 100 Hz (physics step). `lidar_model` interpolates between steps and extrapolates up to 30 ms past the newest one.
- Grazing loss and mixed pixels are computed from neighbouring beams, not from the map geometry.
- `lidar_model` needs the bridge on wall-clock time: `use_sim_time: False` in the gym config.
- The gym's 3D car model and wheels stay on the `ego_racecar/*` frames.
- Reset (`/initialpose`) moves the truth, not `/odom`: wheel odometry keeps integrating, as on the car. With `debug_map_to_odom:=static` the overlay is then off until the next launch.
