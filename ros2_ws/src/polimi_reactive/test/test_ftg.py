"""Unit tests for the Follow the Gap core on synthetic scans (no ROS, no simulator).

Run: cd ~/ws && colcon test --packages-select polimi_reactive --event-handlers console_direct+
  or: python3 -m pytest src/polimi_reactive/test
"""
import math

import numpy as np
import pytest

from polimi_reactive.ftg import FtgParams, follow_the_gap, longest_run, moving_average
from polimi_reactive.scan_utils import LidarConfig, Mount, ScanGeometry

FOV = math.radians(270.0)


def raycast(segments, n, mount=Mount(), max_range=25.0):
    """Ranges of an n-beam, 270 deg scan from a laser at `mount`, against 2D wall segments (base frame)."""
    theta = -FOV / 2 + np.arange(n) * FOV / (n - 1)
    d = mount.R @ np.stack([np.cos(theta), np.sin(theta), np.zeros(n)])
    ox, oy = mount.t[0], mount.t[1]
    r = np.full(n, np.inf)
    for (x1, y1), (x2, y2) in segments:
        ex, ey = x2 - x1, y2 - y1
        den = d[0] * ey - d[1] * ex
        with np.errstate(divide='ignore', invalid='ignore'):
            t = ((x1 - ox) * ey - (y1 - oy) * ex) / den
            u = ((x1 - ox) * d[1] - (y1 - oy) * d[0]) / den
        hit = (np.abs(den) > 1e-12) & (t > 0) & (u >= 0) & (u <= 1)
        r = np.where(hit & (t < r), t, r)
    r[r > max_range] = np.inf
    return r, -FOV / 2, FOV / (n - 1)


def run(segments, n=1351, mount=Mount(), params=None, lidar=None):
    r, amin, inc = raycast(segments, n, mount)
    geom = ScanGeometry(lidar or LidarConfig(), mount)
    geom.update(n, amin, inc)
    return follow_the_gap(geom.clean(r), geom, params or FtgParams()), geom


STRAIGHT = [((-5, 1), (30, 1)), ((-5, -1), (30, -1))]
# corridor 2 m wide going ahead, then turning left; the car is at the entry of the turn
# (the opening spans x = 0..2 ahead of it), so the branch going up is visible.
LEFT_TURN = [((-7, -1), (2, -1)), ((2, -1), (2, 10)),     # right wall, then far wall going up
             ((-7, 1), (0, 1)), ((0, 1), (0, 10))]       # left wall, then the inside of the turn
# closed box, every wall closer than r_free (corners at 1.13 m)
BOX = [((0.8, -0.8), (0.8, 0.8)), ((0.8, 0.8), (-0.8, 0.8)),
       ((-0.8, 0.8), (-0.8, -0.8)), ((-0.8, -0.8), (0.8, -0.8))]


def test_longest_run():
    assert longest_run(np.array([0, 1, 1, 0, 1, 1, 1, 0], bool)) == (4, 7)
    assert longest_run(np.zeros(5, bool)) == (0, 0)
    assert longest_run(np.ones(4, bool)) == (0, 4)


def test_moving_average_keeps_length():
    r = np.arange(10, dtype=float)
    assert len(moving_average(r, 5)) == 10
    assert moving_average(r, 1).tolist() == r.tolist()


def test_straight_corridor_goes_straight_fast():
    res, _ = run(STRAIGHT)
    assert res.ok
    assert abs(math.degrees(res.steering)) < 3.0
    assert res.speed == pytest.approx(1.5)


def test_off_center_does_not_steer_into_near_wall():
    walls = [((-5, 0.4), (30, 0.4)), ((-5, -1.6), (30, -1.6))]   # left wall 0.4 m away
    res, _ = run(walls)
    assert res.ok
    assert res.steering <= 0.0


def test_left_turn_steers_left():
    res, _ = run(LEFT_TURN)
    assert res.ok
    assert res.steering > math.radians(5.0)


def test_closed_box_stops():
    res, _ = run(BOX)
    assert not res.ok
    assert res.speed == 0.0


def test_resolution_independent():
    a, _ = run(LEFT_TURN, n=1351)
    b, _ = run(LEFT_TURN, n=819)
    assert abs(math.degrees(a.steering - b.steering)) < 3.0


def test_mount_offset_and_upside_down():
    upright, _ = run(LEFT_TURN, mount=Mount.planar(x=0.275))
    flipped, geom = run(LEFT_TURN, mount=Mount.planar(x=0.275, inverted=True))
    assert np.all(np.diff(geom.beam_angle[geom.in_fov]) < 0)   # beam order reversed in the car frame
    assert abs(math.degrees(upright.steering - flipped.steering)) < 1.0


def test_mask_removes_beams():
    lidar = LidarConfig(mask_deg=(-5.0, 5.0, 30.0, 20.0))         # second pair is lo >= hi: ignored
    _, geom = run(STRAIGHT, lidar=lidar)
    a = np.degrees(geom.beam_angle)
    assert not geom.in_fov[np.abs(a) < 4.9].any()
    assert geom.in_fov[(a > 20.5) & (a < 29.5)].all()


def test_pure_pursuit_steers_less_than_angle_mode_far_away():
    a, _ = run(LEFT_TURN, params=FtgParams(steering_mode='angle'))
    p, _ = run(LEFT_TURN, params=FtgParams(steering_mode='pure_pursuit'))
    assert 0.0 < p.steering <= a.steering + 1e-9


def test_invalid_params_rejected():
    with pytest.raises(ValueError):
        FtgParams(speeds=(1.0,)).validate()
    with pytest.raises(ValueError):
        FtgParams(target_mode='nope').validate()
    with pytest.raises(ValueError):
        LidarConfig(mask_deg=(1.0, 2.0, 3.0)).mask_pairs_rad()
