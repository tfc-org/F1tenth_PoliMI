# Car

The car is not built yet, so nothing on this page has run on hardware. It records how the bringup is meant to work and what is still missing. On the car the stack runs in the `jet` container (no simulator, host networking).

Until then, the [simulator](simulator.md) stands in for it with the same topics and frames.

## Bringup

Starts the drivers: VESC, joystick teleop, the command mux and the static transform to the LiDAR.

```bash
docker compose build jet
docker compose up -d jet
docker compose exec jet bash
ros2 launch f1tenth_stack no_lidar_bringup_launch.py
```

The VESC packages (`vesc_driver`, `vesc_ackermann`) build with the rest of the workspace: `cb`.

## Before the first run

Things the upstream bringup assumes or leaves to us:

- udev rule on the Jetson for `/dev/sensors/vesc` (expected by f1tenth's `vesc.yaml`).
- LiDAR driver for the chosen sensor (f1tenth_system only ships Hokuyo / SICK).
- Our configs: VESC gains and servo offset, joystick map, `base_link → laser` transform.
- A real deadman for `/drive`: f1tenth's default `joy_teleop.yaml` doesn't gate autonomy.

## Control path

Two sources can command the car. A mux picks the one with the highest priority that is still sending, so a person with the joystick always overrides the autonomy.

- Joystick → `joy_teleop` → `/teleop` (priority 100, LB held).
- Autonomy → `/drive` (priority 10).
- `ackermann_mux` → `/ackermann_cmd` → `ackermann_to_vesc` → VESC. Each input times out after 0.2 s.
- The bringup's remapping `ackermann_cmd_out → ackermann_drive` matches nothing: the mux publishes `ackermann_cmd`.

## Follow-ups

Found while building the simulator, to fix when the car is here:

- LiDAR mount: the bringup hard-codes `base_link → laser` as `0.27 0 0.11`. It should read `ros2_ws/config/car/laser_mount.yaml`, the file the simulator uses ([simulator.md](simulator.md)).
- `vesc.yaml` has `wheelbase: .25`; the simulated odometry uses the gym's 0.3302. Measure the car and align both.
