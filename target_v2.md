# Project targets

This page has two parts:

- **Summer school exercises (esercitazioni):** the topics the professor will teach the students at the summer school, using our car and stack.
- **30L delivery:** what our team has to deliver to get 30 e lode.

The environment is the one in [Project scope](docs/scope.md): a room, a closed track drawn with tape on the floor, no walls. The LiDAR sees the room only. The camera is the only sensor that sees the track.

## Summer school exercises (esercitazioni)

The exercises go from the simplest to the most advanced. Each one builds on the ones before it. Every exercise must run in the simulator first, then on the car.

### 1. Trajectory tracking control (controllo e inseguimento traiettoria)

- **Goal:** the car follows a given path with a feedback controller.
- **Concepts:** vehicle kinematics (bicycle model), path tracking error (lateral and heading), geometric controllers (Pure Pursuit, Stanley), speed control, tuning of gains and look-ahead distance.
- **Two variants, by where the car's position comes from:**
  - **1a. With absolute localization.** The car knows its pose in the room map. The path is given in map coordinates, starting from the simplest case: draw a straight line and drive along it. Then curves and full loops.
  - **1b. With computer vision.** The car has no map. It sees the tape with the camera and follows it directly, in its own frame, for example with a PID on the distance from the track centre.
- **Outcome:** the students see the controller is the same in both variants. Only the source of the reference changes.

### 2. Line recognition (riconoscimento delle linee)

- **Goal:** detect the tape lines in the camera image and give their position on the floor, relative to the car.
- **Concepts:** colour spaces and thresholding, edge detection, perspective transform to a bird's-eye view, camera calibration (intrinsic and extrinsic), line and curve fitting, robustness to light and floor reflections.
- **Outcome:** a node that publishes the track lines (or the track centre line) in the car frame. This is the input of exercise 1b.

### 3. Localization on a map (AMCL)

- **Goal:** build a map of the room, then find the car's pose in that map while it drives.
- **Concepts:**
  - **Mapping:** graph-based SLAM (pose graph, scan matching, loop closure), for example with `slam_toolbox`.
  - **Localization:** Monte Carlo localization (particle filter), as in AMCL: prediction from odometry, correction from LiDAR scans, resampling.
  - Why the map is of the room and not of the track.
- **Outcome:** the car knows its pose in the room map. This is the input of exercise 1a.

### 4. Planning (pianificazione)

- **Goal:** compute the path the car follows, instead of drawing it by hand.
- **Concepts:** track representation (centre line and width), path smoothing, curvature, speed profile from the car's friction and acceleration limits, an introduction to the racing line (shortest path versus minimum curvature).
- **Outcome:** a path and speed profile that the controller of exercise 1 follows.

### 5. Hybrid localization (localizzazione ibrida)

- **Goal:** combine the sensors so the pose is better than any single one.
- **Concepts:** sensor fusion with a Kalman filter (EKF): wheel odometry, IMU, LiDAR localization on the room map, camera detection of the tape. What each sensor is good and bad at, and how the filter weighs them.
- **Outcome:** a pose that is accurate both in the room (LiDAR) and relative to the track lines (camera).

## 30L delivery

To get 30 e lode we deliver **a state-of-the-art base platform** and **one advanced topic**: either racing-line planning or hybrid localization.

### Base platform (required)

A complete car and stack that works end to end. This is also what the summer school exercises run on.

- **Hardware:** the car built and wired as in the [Master BOM](hardware/bom/master_bom.xlsx): Jetson Orin Nano, Orbbec Pulsar SL450 LiDAR, Orbbec Gemini 335L camera, VESC, Traxxas chassis.
- **Software:** ROS 2 stack in Docker, the same on the simulator and on the car:
  - **Drivers:** our fork of `f1tenth_system`, extended with all our drivers: VESC (motor, servo, odometry), joystick teleop with a deadman and `ackermann_mux` (the joystick always overrides the autonomy), the Pulsar SL450 LiDAR driver and the Gemini 335L camera driver (`orbbec_camera`).
  - **Simulator:** f1tenth_gym and f1tenth_gym_ros, extended with our `polimi_sim` so the simulator behaves like the car. Every exercise can be tried before the car.
  - **Mapping:** SLAM of the room (for example `slam_toolbox`).
  - **Localization:** AMCL in the saved room map.
  - **Line detection:** the camera detects the tape lines and publishes the track centre as a path in the car frame.
  - **Path following:** a PID controller on the lateral (and heading) error between the car's pose and a path. It does not care where either comes from:
    - **Path:** a `nav_msgs/Path` on one topic, in any frame. It can be drawn by the user (map frame), come from line detection (car frame), or be the optimized racing line of option A (map frame).
    - **Pose:** read from TF in the path's frame. It can come from AMCL, from the hybrid localization of option B, or from the simulator's ground truth. A path in the car frame needs no map pose.
    - **Controller:** any node with the same inputs (path, pose) and output (`/drive`) can replace the PID, for example Pure Pursuit.
    - **Offline and online paths:** a hand-drawn path or the racing line is computed once, saved to a file and published once as a closed loop (latched). The line detection path is recomputed from every camera frame and covers only a short stretch ahead of the car. The PID computation is the same for both.
    - **Full path or fragment:** the PID only needs the stretch around the car: the closest point gives the error, a few points ahead give the heading of the path. On a full loop it searches the closest point only in a window after the last one it used, so it is cheap and cannot jump to another part of the track that runs close by. On a fragment it searches all of it.
    - **Stale path:** if an online path stops updating (the camera loses the tape), the PID stops the car. A latched offline path is never stale.
- **Safety:** a person can always stop or take over the car, and the car brakes on its own before a collision. Both work on the car and in the simulator:
  - **Joystick emergency stop:** a joystick button latches zero speed and zero steering on top of every other source. It holds until someone resets it on purpose.
  - **Joystick deadman:** the autonomy drives only while a person holds the navigation deadman (RB). Letting go stops the car. The teleop has its own deadman (LB).
  - **Joystick takeover:** `ackermann_mux` gives the joystick priority over `/drive`, so a person can always override the autonomy.
  - **Automatic emergency braking (AEB):** a safety node computes the time to collision from the LiDAR and brakes under a threshold, whatever is driving.
- **Documentation:** setup, how to run each part, and design decisions, so another team or the professor can use the platform without us.
- **Done when:** the car maps the room, localizes with AMCL, and with the PID drives full laps of the taped track without leaving the lines, both on the track centre seen by the camera and on a path drawn in the map, on the car and in the simulator. Each safety feature is tested on the car: pressing the emergency stop, releasing the deadman, taking over with the joystick, and an obstacle in front all stop the car or hand it to the person.

### Advanced topic, option A: racing-line planning (pianificazione ottimizzando le racing line)

- **What:** compute the optimal racing line inside the tape lines, and the speed profile along it, then race it.
- **How:**
  - Get the track boundaries in map coordinates, by mapping the tape lines seen by the camera into the room map.
  - Optimize the line: minimum curvature, then minimum lap time, with the car's limits (friction, acceleration, steering). The TUM `global_racetrajectory_optimization` method is the reference.
  - Track the line at speed with a controller that copes with high speed (tuned Pure Pursuit, or MPC).
- **Done when:** the car laps faster on the optimized line than on the centre line, without leaving the lines. Measured as lap times and line crossings over several laps.

### Advanced topic, option B: hybrid localization (localizzazione ibrida)

- **What:** a localization that fuses all sensors, and stays accurate at racing speed.
- **How:**
  - Fuse wheel odometry, IMU and LiDAR localization in the room map with an EKF (for example `robot_localization`).
  - Add the camera: the detected tape lines correct the pose relative to the track, where the LiDAR is weak (open room, few features, or furniture that moved).
  - Handle failures: one sensor drops out or gives a wrong reading, and the pose stays usable.
- **Done when:** the fused pose is more accurate and more robust than LiDAR-only localization. Measured against a ground truth (the simulator, or marks on the floor) at increasing speeds.
