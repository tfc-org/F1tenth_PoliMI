# Camera Comparison for F1TENTH

*Last updated: 7 October 2026*

> **Decision (Master BOM, 7 Oct 2026):** **Orbbec Gemini 335L**, €420 from OpenElab (DigiKey Italy at €408 as a second source). The Intel RealSense D435i stays in the BOM as an unselected alternative.
>
> **Integration to-dos:** Orbbec's ROS 2 driver (`orbbec_camera` from [OrbbecSDK_ROS2](https://github.com/orbbec/OrbbecSDK_ROS2), launch file `gemini_330_series.launch.py`) and its udev rules; the camera mount and the `base_link → camera_link` transform; a USB 3 port on the Orin Nano (its only Ethernet port goes to the LiDAR). See [car.md](../software/car.md).

## Brief

The [scope](../scope.md) puts the track on the floor as tape. The LiDAR can't see it, so a camera has to find the tape lines and the car has to stay inside them. The LiDAR maps the room on its own.

What that asks of the camera, most important first:

| Need | Why |
|---|---|
| **Global-shutter colour** | At 5–8 m/s a rolling shutter skews and smears the tape lines, worst in corners. The tape colour isn't decided yet, so colour matters. |
| **Wide field of view, ≥ 60 fps** | Both lines must stay in view near the car and through corners. At 8 m/s, 30 fps means 27 cm travelled per frame. |
| **Accurate pixel → floor projection** | To know where the lines are relative to the car. Needs good factory intrinsics and the camera's pitch and roll relative to the floor at every frame: braking and accelerating pitch the car, so a fixed mount calibration isn't enough at speed. |
| **Depth aligned to colour, and an IMU** | To measure that pitch and roll each frame: fit the floor plane in the depth image, or use the IMU. |
| **Hardware timestamps** | 10 ms of timestamp error at 8 m/s is 8 cm. |
| **USB 3, light** | The Orin Nano's only Ethernet port goes to the LiDAR. 1/10 car. |

**The D435i's weak spot** for this scope: its colour camera is **rolling shutter**, 1080p at 30 fps, 69° × 42°. Its depth, IR cameras and IMU are fine.

## Ranking

| # | Camera | Price | Notes |
|---|---|---|---|
| 1 | **[Orbbec Gemini 335L](https://store.orbbec.com/products/gemini-335l)** / [336L](https://store.orbbec.com/products/gemini-336l) | €420 (335L, OpenElab); €514.95 / €586.31 at [MyBotShop](https://www.mybotshop.de/Orbbec-Gemini-335L_1); $359 / $379 at Orbbec's store | Global-shutter colour 1280×800 up to 60 fps, 94° × 68°; depth aligned to colour in the camera; IMU up to 1 kHz; depth from 0.17 m, 95 mm baseline; 133 g, IP65. The 336L adds an IR-pass filter on the depth cameras, which helps depth on glossy floors. |
| 2 | **[RealSense D436](https://www.generationrobots.com/en/404465-realsense-d436-depth-camera.html)** | €576 | Same capabilities (global-shutter colour 1280×800 @ 60, 90° × 65°, aligned depth, IMU) in the D435i's body, with the same driver and topics. |
| 3 | **[Arducam B0385](https://welectron.com/Arducam-B0385-120fps-Global-Shutter-Color-USB-Camera-Board)** (OV9782) + an IMU board | €68.90 + ~€25 | Global-shutter colour is all segmentation needs. No depth, no factory calibration, no hardware IMU sync. USB 2, so 100 fps only as MJPEG (uncompressed drops to 10 fps). Being discontinued at some shops. |
| 4 | **[Luxonis OAK-D W](https://shop.luxonis.com/products/oak-d-w)** (OV9782 colour) | $479 (≈ €522 with import VAT, before shipping) | Global-shutter colour, 127° wide, can run a segmentation network on the camera. Strong fisheye distortion, weaker depth, less common in F1TENTH. |
| 5 | **RealSense D435i** | €405 | Rolling-shutter 30 fps colour. Usable only if the tape shows up on its global-shutter IR cameras (e.g. white tape on a dark floor). |

### Skipped

- **Gemini 335 / 336 (short baseline), OAK-D Lite, OAK-D S2:** rolling-shutter colour, no better than the D435i.
- **ZED Mini / ZED 2i:** rolling shutter, and depth runs on the Orin's GPU. The global-shutter ZED X family needs a GMSL2 capture card, which breaks the budget.
- **RealSense D455:** global-shutter colour and IMU, but bigger, ~€536 and up, and its minimum depth of 0.4–0.5 m misses the floor right in front of the car.

## Notes

- **Colour-camera offset:** on all these depth cameras the colour camera sits beside the left IR camera, which is the depth origin. On the Gemini 335L it is 23.75 mm along x; the IMU is at (7.866, 1.068, −14.248) mm ([Orbbec coordinate systems](https://doc.orbbec.com/documentation/Orbbec%20Gemini%20330%20Series%20Documentation/Coordinate%20Systems%20(Stereo%20Vision%203D%20Camera))). The offsets are calibrated at the factory and published as transforms, and the floor calibration absorbs them. Mount with the colour lens on the car's centreline for a symmetric view.
- **Projection:** fitting a floor plane to the depth image is more robust than reading depth at each tape pixel, because stereo depth on a floor seen at a shallow angle is noisy.
- **335L vs 336L:** the 336L's IR-pass filter blocks visible light on the IR cameras. With the projector off under LED room lighting their images would be dark, so the 335L is the safer choice if the IR images are ever used on their own.
