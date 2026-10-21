# Project scope

*Last updated: 21 October 2026*

This page says what the car has to do, in what environment, and what we deliver: the summer school exercises (esercitazioni) the professor will teach the students on our car and stack, and the 30L delivery, what our team has to deliver to get 30 e lode.

## Environment

- The car runs **indoors, in a room**.
- The track is a **closed loop drawn on the floor with tape**. It has no walls or barriers: nothing along the track rises above the floor.
- The only things that stand up from the floor are the room itself: its walls, furniture and anything else in it.

This replaces the earlier assumption of a track bounded by walls (flexible ducts), which a 2D LiDAR could see and map directly.

## What the car must do

1. **Map the room with SLAM.** The map is of the room, not of the track.
2. **Detect the taped track and stay inside its lines** while driving.

## What follows from the environment

- **The LiDAR cannot see the track.** Tape is flat on the floor and the LiDAR scans a horizontal plane above it. The LiDAR sees the room only.
- **A camera is required.** The track exists only as something visible on the floor, so it can only be sensed by vision.
- **No track walls to buy.** The track is tape, so the ducts (track material) are deselected in the BOM.
- **Leaving the track is not a collision.** Nothing physical stops the car when it crosses a line, so staying inside the lines has to be measured, not detected by a crash.

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

- **Hardware:** the car built and wired as in the [Master BOM](../hardware/bom/master_bom.xlsx): Jetson Orin Nano, Orbbec Pulsar SL450 LiDAR, Orbbec Gemini 335L camera, VESC, Traxxas chassis.
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

## Variable by design

The stack must not depend on any of these:

- **Track layout:** it varies. Any closed loop drawn as two boundary lines.
- **Room:** not too large, mapped with SLAM on site.

## Not defined yet

- **Floor:** material and colour. Ideally variable too.
- **Tape:** colour and width.

## Open items (OI)

Decisions and checks the scope leaves open. Each row gives the options and a suggested answer; nothing is decided until the row says so. **[DECIDE]** is a choice for the team, **[VERIFY]** a fact to check.

| ID | Type | Item | Options and suggestion | Needed by | Status |
|---|---|---|---|---|---|
| OI-01 | [DECIDE] | **Advanced topic: option A (racing line) or option B (hybrid localization).** | Both need the tape lines in map coordinates (OI-03). A also needs the vehicle parameters (friction, CoG height), the TUM optimizer, a controller that holds at speed, and a localization that keeps up at speed; it is easy to prove (lap times, line crossings), but the gain is small in a small room. B needs an EKF, a camera correction that observes only the lateral offset and heading relative to the tape, and handling of sensor failures; it is harder to prove on the car (needs a ground truth) and overlaps exercise 5. | After the base platform runs | **Held** until the base platform runs (21 Oct 2026) |
| OI-02 | [DECIDE] | **Frame of the line-detection path:** car frame (`base_link`) or `odom`. | Suggested: `odom`, transformed at the image time stamp. It compensates the camera latency, keeps a fragment valid between frames, and lets the stale-path rule become "keep going on the last path for a short distance, then stop". Alternative: keep `base_link` and let the PID look up the transform at the image time. The path-following contract (any frame) does not change. | Line detection, path following | Open |
| OI-03 | [DECIDE] | **Where the "path drawn in the map" comes from.** The tape is not in the LiDAR map, so the path cannot be drawn by hand inside it. | Suggested for the base platform: **teach and repeat**: drive the camera follower (1b) slowly with AMCL running, record the poses in the map, smooth them and save them as the path. Later, for A or B: **tape mapping**: project the detected tape into the map and build the two boundary lines. | Base platform done-when, exercise 1a | Open |
| OI-04 | [DECIDE] | **Open paths.** Exercise 1a starts from a straight line, but offline paths are published as closed loops. | Add an open-path mode: the PID stops the car at the end of the path. | Path following | Open |
| OI-05 | [DECIDE] | **Form of the PID.** A PID on the lateral error alone oscillates as speed rises. | Lateral and heading error with a look-ahead point (Stanley-like); Pure Pursuit as the drop-in for higher speed. | Path following | Open |
| OI-06 | [DECIDE] | **Line detection method.** | (a) Image space: colour threshold, bird's-eye view, sliding windows, polynomial fit (the classic exercise 2). (b) Floor points: segment the tape, project the pixels onto the floor, fit and track the lines in `odom` (also feeds tape mapping, OI-03). (c) A learned segmentation, only if thresholds fail on the real floor. Hard cases for all: hairpins where three or four lines are visible, only one line visible, glare. First data: phone video of the real tape. | Exercise 2, base platform | Open |
| OI-07 | [DECIDE] | **Localization node.** | `nav2_amcl` (named by the scope; needs an image rebuild), `slam_toolbox` in localization mode (already in the image), or MIT `particle_filter` if AMCL is too slow at speed. Risks: a rectangular room is symmetric (always give the initial pose), people standing around the track, furniture moved after mapping. | Exercise 3, base platform | Open |
| OI-08 | [DECIDE] | **EKF for `odom`** (wheel odometry and the camera IMU, `robot_localization`) in the base platform. | Suggested: yes. It helps exercise 1a and both options, and is the first half of exercise 5. | Base platform | Open |
| OI-09 | [VERIFY] | **Safety with `ackermann_mux` locks** (supported by the mux in `f1tenth_system`). | Emergency stop: a latched lock above the joystick. Autonomy deadman: a lock with a timeout between `/drive` and the joystick, released while RB is held (today RB's `autonomous_control` publishes to `/dev/null`, so the autonomy is not gated). AEB: an input between `/drive` and the joystick that brakes under a time-to-collision threshold, so a person can still drive the car away. Check how locks behave in this mux. | Safety | Open |
| OI-10 | [VERIFY] | **One image rebuild** for `nav2_amcl`, `robot_localization`, `image_transport_plugins` and `cv_bridge`, together with the simulator fork's rebuild. | Check that `cv_bridge` does not install apt's `python3-opencv`, which clashes with the gym's pip `cv2`. | Before the stack nodes | Open |
| OI-11 | [DECIDE] | **Off-track report from the stack's own estimate (optional).** On the car, leaving the lines is judged by the people watching: nothing in software enforces or measures it, and there is no external tracking. | Optional: a node that compares the car's footprint at the pose the stack is running on (map or odom) with the tape lines (tape map or detected lines) and reports when it believes the car is off the track. It only reports, never stops the car, and it shows what the stack believes, not the truth. | Optional, once the tape lines are in map or odom | Open (optional) |
| OI-12 | [DECIDE] | **Exercises in the simulator.** "Every exercise must run in the simulator first, then on the car" (Summer school exercises) and "Every exercise can be tried before the car" (Base platform, Simulator) make the exercises a requirement for the sim, while the exercises are reference for what the summer school will teach. | Suggested (user, 21 Oct 2026): the exercises are reference only, not required in the simulator or in the base platform; the simulator covers what the base platform's done-when needs. Optional sim additions for the exercises are listed in the simulation plans (plan 01.5, O-25). Reword both sentences once confirmed. | Simulation plans | Open |
