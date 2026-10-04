# Car

Not built yet. Runs in the `jet` container (no simulator, host networking).

## Bringup

```bash
docker compose build jet
docker compose up -d jet
docker compose exec jet bash
ros2 launch f1tenth_stack no_lidar_bringup_launch.py
```

The VESC packages (`vesc_driver`, `vesc_ackermann`) build with the rest of the workspace: `cb`.

## Before the first run

- udev rule on the Jetson for `/dev/sensors/vesc` (expected by f1tenth's `vesc.yaml`).
- LiDAR driver for the chosen sensor (f1tenth_system only ships Hokuyo / SICK).
- Our configs: VESC gains and servo offset, joystick map, `base_link → laser` transform.
- A real deadman for `/drive`: f1tenth's default `joy_teleop.yaml` doesn't gate autonomy.

## Control path

- Joystick → `joy_teleop` → `/teleop` (priority 100, LB held).
- Autonomy → `/drive` (priority 10).
- `ackermann_mux` → `/ackermann_drive` → VESC. Each input times out after 0.2 s.
