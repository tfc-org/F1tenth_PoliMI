# Project scope

*Last updated: 5 October 2026*

This page says what the car has to do and in what environment. It does not say how we will do it: those choices are still open.

## Environment

- The car runs **indoors, in a room**.
- The track is a **closed loop drawn on the floor with tape**. It has no walls or barriers: nothing along the track rises above the floor.
- The only things that stand up from the floor are the room itself: its walls, furniture and anything else in it.

This replaces the earlier assumption of a track bounded by walls (flexible ducts), which a 2D LiDAR could see and map directly.

## What the car must do

1. **Map the room with SLAM.** The map is of the room, not of the track.
2. **Detect the taped track and stay inside its lines** while driving.

## Our addition

3. **SLAM on the taped track with computer vision as the input**, not the LiDAR.

## What follows from the environment

- **The LiDAR cannot see the track.** Tape is flat on the floor and the LiDAR scans a horizontal plane above it. The LiDAR sees the room only.
- **A camera is required.** The track exists only as something visible on the floor, so it can only be sensed by vision.
- **No track walls to buy.** The track is tape, so the ducts (track material) are deselected in the BOM.
- **Leaving the track is not a collision.** Nothing physical stops the car when it crosses a line, so staying inside the lines has to be measured, not detected by a crash.

## Not defined yet

- The track layout, and whether it is drawn as two boundary lines or as one line.
- The tape: colour and width. The floor: material and colour.
- The room: size and what is in it.
