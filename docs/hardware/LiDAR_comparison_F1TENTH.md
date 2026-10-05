# LiDAR Comparison for F1TENTH

*Last updated: 23 September 2026*

> **Scope change (5 Oct 2026):** the track is now tape on the floor of a room ([Project scope](../scope.md)). The LiDAR cannot see it and maps the room instead, so where this page says "track" about range or SLAM, read "room". The pick below is unchanged.

## Brief

We need to pick a LiDAR for an F1TENTH car: a 1/10-scale self-driving car that runs SLAM and drives at high speed. The seven candidates below come from RobotShop EU. Specs were checked against each product page, and missing values (scan rates, drivers) were filled in from the manufacturers' datasheets.

**Key point:** for F1TENTH, **scan rate (Hz)** matters far more than range. At 8 m/s, a 10 Hz LiDAR lets the car move 80 cm between scans, which makes scan matching and localization much harder. Range beyond about 10 m barely matters on a track.

## Product links

| # | Model | RobotShop EU |
|---|---|---|
| 1 | Orbbec Pulsar SL450 | [Link](https://eu.robotshop.com/products/orbbec-pulsar-sl450-single-line-lidar-robotic-navigation) |
| 2 | Richbeam Lakibeam 1L | [Link](https://eu.robotshop.com/products/lakibeam-1l-dtof-industry-grade-single-line-lidar) |
| 3 | Richbeam Lakibeam 1 | [Link](https://eu.robotshop.com/products/lakibeam-1-dtof-industry-grade-single-line-lidar) |
| 4 | Richbeam Lakibeam 1S | [Link](https://eu.robotshop.com/products/lakibeam-1s-dtof-industry-grade-single-line-2d-lidar) |
| 5 | Slamtec RPLIDAR S3 | [Link](https://eu.robotshop.com/products/slamtec-rplidar-s3-360-laser-scanner-40-m) |
| 6 | LSLIDAR N301 | [Link](https://eu.robotshop.com/products/lslidar-n301-navigation-obstacle-avoidance-lidar) |
| 7 | Slamtec RPLIDAR A2M12 | [Link](https://eu.robotshop.com/products/rplidar-a2m12-360-laser-range-scanner) |

## Spec comparison

| Spec | [Orbbec SL450](https://eu.robotshop.com/products/orbbec-pulsar-sl450-single-line-lidar-robotic-navigation) | [Lakibeam 1L](https://eu.robotshop.com/products/lakibeam-1l-dtof-industry-grade-single-line-lidar) | [Lakibeam 1](https://eu.robotshop.com/products/lakibeam-1-dtof-industry-grade-single-line-lidar) | [Lakibeam 1S](https://eu.robotshop.com/products/lakibeam-1s-dtof-industry-grade-single-line-2d-lidar) | [Slamtec S3](https://eu.robotshop.com/products/slamtec-rplidar-s3-360-laser-scanner-40-m) | [LSLIDAR N301](https://eu.robotshop.com/products/lslidar-n301-navigation-obstacle-avoidance-lidar) | [RPLIDAR A2M12](https://eu.robotshop.com/products/rplidar-a2m12-360-laser-range-scanner) |
|---|---|---|---|---|---|---|---|
| Price (RobotShop EU) | €531 | €549 | €439 | €340 | €549 | €1,100 (on demand) | €227 |
| **Max scan rate** | **40 Hz** | 30 Hz | 30 Hz | 20 Hz | 20 Hz | 20 Hz | 15 Hz |
| Resolution @ max rate | 0.2° | 0.25° | 0.25° | 0.5° | 0.225° | 0.36° | ~0.225°+ |
| Sample rate | 72 kHz | 45 kHz | up to 43.2 kHz | 14.4–18 kHz | 32 kHz | 20 kHz | 16 kHz |
| FOV | 270° | 270° | 270° | 270° | 360° | 360° | 360° |
| Range (70–90% refl.) | 45 m | 40 m | 25 m | 15 m | 40 m | 30 m | 12 m |
| Range (10% refl.) | 15 m | 20 m | 15 m | 10 m | 15 m | – | – |
| Accuracy | ±2 cm | ±2 cm | ±2 cm | ±2 cm | ±3 cm | ±3 cm | 1–2.5% of range |
| Principle | dToF | dToF | dToF | dToF | dToF | ToF | Triangulation |
| Interface | Ethernet (per protocol doc) | Ethernet + USB-C | Ethernet + USB-C | Ethernet + USB-C | UART 1 Mbps | Ethernet | UART 256 kbps |
| Supply voltage | see datasheet | 9–36 V | 9–36 V | 6–36 V | 5 V | 9–36 V | 5 V |
| Weight | ~320 g | 160 g | 160 g | 160 g | 115 g | 406 g | 190 g |
| IP rating | IP65 | IP65 | IP65 | IP65 | – | IP67 | – |
| ROS 2 | Yes (Orbbec SDK) | Yes | Yes | Yes | Yes | Yes | Yes |

**Benchmark:** the standard F1TENTH LiDAR, the [Hokuyo UST-10LX](https://www.robotshop.com/en/hokuyo-ust-10lx-scanning-laser-rangefinder.html) (~€1,200 in our Master BOM), runs at **40 Hz with 0.25° resolution over 270°**. That's the target to match.

## Distance the car travels between scans

This is the number to watch for high-speed SLAM and localization:

| Scan rate | At 5 m/s | At 8 m/s |
|---|---|---|
| 10 Hz | 50 cm | 80 cm |
| 20 Hz | 25 cm | 40 cm |
| 30 Hz | 17 cm | 27 cm |
| 40 Hz | 12.5 cm | 20 cm |

## Verdict for F1TENTH

### Best overall: [Orbbec Pulsar SL450](https://eu.robotshop.com/products/orbbec-pulsar-sl450-single-line-lidar-robotic-navigation)

- It's the only candidate that matches the Hokuyo's 40 Hz. The datasheet lists rotation frequencies of 15, 20, 25, 30 and 40 Hz.
- It keeps 0.2° resolution even at 40 Hz, thanks to its 72 kHz sample rate. It also has multi-echo noise filtering.
- **Downsides:** it weighs 320 g, twice as much as the Lakibeams. It's also newer (launched at ProMat in March 2025), so there's less community troubleshooting than for Slamtec.

### Best value: [Lakibeam 1](https://eu.robotshop.com/products/lakibeam-1-dtof-industry-grade-single-line-lidar)

- 30 Hz at 0.25° for €439, 160 g, with Ethernet or USB-C.
- It accepts 9–36 V, so it can run straight from a 3S LiPo.
- Richbeam's ROS 2 driver listens to the LiDAR's UDP packets and publishes to `/scan`. The recommended setup is Ubuntu 22.04 with ROS 2 Humble.
- 25 m of range is plenty for a track. The 1L only adds range (40 m), which we don't need, for €110 more.

### Skip these for high speed

- **Lakibeam 1S:** 0.5° resolution at 20 Hz is too coarse.
- **Slamtec S3:** a good sensor and the lightest, but capped at 20 Hz, and resolution drops to 0.225° at that rate. Better suited to slower robots.
- **LSLIDAR N301:** twice the price, the heaviest, and only 20 Hz with 0.36° resolution. It's built for forklifts.
- **RPLIDAR A2M12:** cheap, but 15 Hz max, 12 m range, triangulation-based, and on a slow UART link. Fine for a slow prototype, not for racing.

### Note on FOV

The 360° units give no advantage on an F1TENTH car. The chassis and electronics block the rear of the scan, so 270° is the norm.

## Recommendation

If budget allows, **go with the SL450**. If you want a safer, lighter and cheaper option with a proven driver, the **Lakibeam 1** is a very reasonable second choice.
