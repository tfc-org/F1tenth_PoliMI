# Reactive control: Follow the Gap

Package `ros2_ws/src/polimi_reactive`, node `gap_follow`: `/scan` → `/drive`. No map, no localization: each scan is handled on its own. It is the explorer for mapping and, later, the fallback controller.

## Run (sim)

```bash
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && source /etc/bashrc_polimi && sim"          # terminal 1
docker compose exec arm bash \
  -c "source /opt/ros/humble/setup.bash && source /etc/bashrc_polimi && cb && ros2 launch polimi_reactive gap_follow.launch.py"   # terminal 2
```

- `cb` is only needed the first time and after adding files: the build uses `--symlink-install`, so edits to the Python code and to `config/ftg.yaml` apply on the next launch.
- Stop with `Ctrl-C`: the node sends a zero command on exit (the sim keeps applying the last `/drive` forever).
- Pause without killing it: `ros2 param set /gap_follow enabled false` (sends one stop, then stays silent).
- Reset after a crash: see [Simulator → Reset position](simulator.md#reset-position).

Launch arguments: `lidar_config` (default `~/ws/config/lidar/sl450.yaml`), `params` (default the package's `config/ftg.yaml`), `base_frame` (default `ego_racecar/base_link`), `scan_topic`, `drive_topic`.

## What to look at in Foxglove

3D panel, display frame `ego_racecar/base_link` (or `map`), enable `/ftg/markers`:

| Marker | Meaning |
|---|---|
| Red points | Safety bubble around the closest obstacle |
| Green points | The gap that was chosen |
| Blue sphere | Target point |
| Yellow arrow | Steering command (longer = faster) |

When it misbehaves, the markers show which step made the bad choice: a bubble that is too small, a gap on the wrong side, a target too close to a corner.

## Algorithm

Code: `polimi_reactive/ftg.py` (plain numpy, unit-tested in `test/test_ftg.py`). Once per scan:

1. **Preprocess.** NaN / inf / closer than `lidar.range_min` → no return. Cap at `ftg.r_max`, moving average over `ftg.smooth_deg`, keep only the `lidar.fov_*` window minus the `lidar.mask_deg` sectors.
2. **Closest point** in the window, distance `d`.
3. **Safety bubble.** Every beam within `asin(R / d)` of the closest one is set to 0 (`R = ftg.bubble_radius`).
4. **Largest gap.** Longest run of beams with `r > ftg.r_free`. No gap → stop.
5. **Target** (`ftg.target_mode`): `farthest`, `center`, or `farthest_smoothed` (default). When several beams are equally deep (all capped at `r_max`), the middle of that run is used, not its first beam.
6. **Steering** (`ftg.steering_mode`): `angle` (default) steers at the target's angle from the car; `pure_pursuit` uses `atan(2 L sin α / L_d)` with `L_d` clamped to `[lookahead_min, lookahead_max]`. Not toward a side closer than `ftg.side_clearance`. Clipped to `ftg.max_steer`, then low-passed with time constant `steer_tau`.
7. **Speed** from `|steering|`: `speeds[k]` below `speed_angles_deg[k]`, the last entry above all, capped at `ftg.v_max`.

Beam angles come from each `LaserScan` message, and the LiDAR mount comes from TF (`base_frame` ← scan frame): the sim publishes `ego_racecar/base_link → ego_racecar/laser`, the car's `f1tenth_stack` bringup publishes `base_link → laser`. All angles in the configs are in the car frame (0 = ahead, + = left), so the same code and configs work on 819 or 1351 beams, and with the LiDAR offset, rotated or upside down. If the TF is missing for `tf_timeout` s, the node warns and assumes the laser sits at `base_frame`.

## Tuning

Live, no restart (applies on the next scan; invalid values are refused):

```bash
ros2 param set /gap_follow ftg.v_max 1.0
ros2 param set /gap_follow ftg.bubble_radius 0.35
ros2 param set /gap_follow ftg.target_mode center
ros2 param dump /gap_follow          # current values, to copy back into config/ftg.yaml
```

Floats need a decimal point (`1.0`, not `1`): ROS 2 refuses an integer for a double parameter.

| Symptom | Try |
|---|---|
| Clips corners / wall edges | Larger `bubble_radius`; `target_mode: center`. The real fix is the disparity extender (next step). |
| Weaves on straights | Larger `steer_tau`; `target_mode: farthest_smoothed` with a wider `target_window_deg`. |
| Turns too late | Larger `r_max` (a wall 4 m ahead only looks closer than open space if `r_max` > 4 m); lower `speeds`. |
| Stops in tight spots ("no gap") | Lower `r_free`. |
| Steers toward a wall it drives along | Larger `side_clearance`. |

## On the car

```bash
ros2 launch polimi_reactive gap_follow.launch.py base_frame:=base_link
```

- `/drive` enters `ackermann_mux` at priority 10, under the joystick (100, LB held). Each input times out after 0.2 s, so killing the node stops the car.
- Measure the real LiDAR mount and set it in the bringup's static transform (and in `sim_sl450.yaml`).
- Fill `lidar.mask_deg` with the sectors the chassis blocks once the SL450 is mounted.

## Not done yet

- No AEB (time-to-collision braking): next step, as its own node.
- Disparity extender: fixes corner clipping.
- The sim's `/scan` runs at 250 Hz on a 100 Hz physics step; the SL450 gives 40 Hz. Re-check `steer_tau` on the car.
