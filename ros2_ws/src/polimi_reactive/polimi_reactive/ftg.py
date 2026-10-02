"""Follow the Gap: one scan in, one steering angle and speed out. Plain numpy, no ROS.

Steps (see docs/software/reactive.md):
  1. preprocess: cap at r_max, smooth, keep the FOV window
  2. closest point
  3. safety bubble around it (cone of half-angle asin(R / d))
  4. largest gap: longest run of beams with r > r_free
  5. target point inside the gap
  6. steering (target angle, or pure-pursuit style), side-wall check
  7. speed from the steering angle
"""
from dataclasses import dataclass, field
import math

import numpy as np

from .scan_utils import ScanGeometry, wrap

TARGET_MODES = ('farthest', 'center', 'farthest_smoothed')
STEERING_MODES = ('angle', 'pure_pursuit')
TIE_TOLERANCE = 0.05  # m: beams this close to the deepest one count as equally deep


@dataclass
class FtgParams:
    r_max: float = 3.0                  # m, decision horizon
    smooth_deg: float = 1.0             # moving-average window
    bubble_radius: float = 0.25         # m, car half-width (0.155) + margin
    r_free: float = 1.2                 # m, a beam is "free" above this
    target_mode: str = 'farthest_smoothed'
    target_window_deg: float = 10.0     # smoothing window for farthest_smoothed
    steering_mode: str = 'angle'
    wheelbase: float = 0.33             # m, pure_pursuit only
    lookahead_min: float = 0.5          # m, pure_pursuit only
    lookahead_max: float = 1.5          # m, pure_pursuit only
    max_steer: float = 0.41             # rad
    speed_angles_deg: tuple = (10.0, 20.0)
    speeds: tuple = (1.5, 1.0, 0.5)     # one more entry than speed_angles_deg
    v_max: float = 1.5                  # m/s, hard cap
    side_clearance: float = 0.2         # m, don't turn toward a side closer than this; 0 disables
    side_window_deg: tuple = (60.0, 100.0)  # side sector checked (mirrored for the right)

    def validate(self):
        if self.target_mode not in TARGET_MODES:
            raise ValueError(f'target_mode must be one of {TARGET_MODES}')
        if self.steering_mode not in STEERING_MODES:
            raise ValueError(f'steering_mode must be one of {STEERING_MODES}')
        if len(self.speeds) != len(self.speed_angles_deg) + 1:
            raise ValueError('speeds needs exactly one more entry than speed_angles_deg')
        if len(self.side_window_deg) != 2:
            raise ValueError('side_window_deg must be [lo, hi]')
        if self.r_free >= self.r_max:
            raise ValueError('r_free must be smaller than r_max')


@dataclass
class FtgResult:
    ok: bool = False
    reason: str = ''
    steering: float = 0.0
    speed: float = 0.0
    closest: int = -1
    bubble: np.ndarray = field(default_factory=lambda: np.zeros(0, bool))
    gap: tuple = (0, 0)                 # half-open [start, end) beam indices
    target: int = -1
    target_xy: tuple = (0.0, 0.0)       # base frame


def n_beams(deg, increment):
    return max(1, int(round(math.radians(deg) / increment))) if increment > 0 else 1


def moving_average(r, k):
    if k <= 1 or len(r) == 0:
        return np.array(r, dtype=float)
    k = min(k, len(r))
    padded = np.pad(r, (k // 2, k - 1 - k // 2), mode='edge')
    return np.convolve(padded, np.ones(k) / k, mode='valid')


def longest_run(mask):
    """Longest run of True as half-open (start, end); (0, 0) if none."""
    m = np.concatenate(([0], np.asarray(mask, dtype=np.int8), [0]))
    d = np.diff(m)
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    if len(starts) == 0:
        return 0, 0
    k = int(np.argmax(ends - starts))
    return int(starts[k]), int(ends[k])


def _deepest(values):
    """Index of the middle of the longest run of near-maximum values (avoids argmax picking an edge on ties)."""
    s, e = longest_run(values >= values.max() - TIE_TOLERANCE)
    return (s + e - 1) // 2


def follow_the_gap(r_clean, geom: ScanGeometry, p: FtgParams) -> FtgResult:
    res = FtgResult(bubble=np.zeros(geom.n, bool))
    fov = geom.in_fov
    if not fov.any():
        res.reason = 'no beams in the FOV window'
        return res

    # 1. preprocess
    r = moving_average(np.minimum(r_clean, p.r_max), n_beams(p.smooth_deg, geom.increment))
    r = np.where(fov, r, 0.0)

    # 2. closest point
    idx = np.flatnonzero(fov)
    i = int(idx[np.argmin(r[idx])])
    d = float(r[i])
    res.closest = i

    # 3. safety bubble: every beam inside the cone that a circle of radius R at distance d covers
    alpha = math.pi / 2 if d <= p.bubble_radius else math.asin(p.bubble_radius / d)
    bubble = fov & (np.abs(wrap(geom.beam_angle - geom.beam_angle[i])) <= alpha)
    r[bubble] = 0.0
    res.bubble = bubble

    # 4. largest gap
    s, e = longest_run(r > p.r_free)
    res.gap = (s, e)
    if e == s:
        res.reason = f'no gap (nothing free beyond {p.r_free:.2f} m)'
        return res

    # 5. target inside the gap
    seg = r[s:e]
    if p.target_mode == 'center':
        j = (s + e - 1) // 2
    elif p.target_mode == 'farthest':
        j = s + _deepest(seg)
    else:
        j = s + _deepest(moving_average(seg, n_beams(p.target_window_deg, geom.increment)))
    res.target = j
    x, y = geom.points(min(float(r_clean[j]), p.r_max), j)
    res.target_xy = (float(x), float(y))

    # 6. steering
    heading = math.atan2(y, x)
    if p.steering_mode == 'angle':
        delta = heading
    else:
        ld = min(max(math.hypot(x, y), p.lookahead_min), p.lookahead_max)
        delta = math.atan(2.0 * p.wheelbase * math.sin(heading) / ld)
    if p.side_clearance > 0.0:
        lo, hi = (math.radians(a) for a in p.side_window_deg)
        near = np.minimum(r_clean, p.r_max)
        left = geom.usable & (geom.beam_angle >= lo) & (geom.beam_angle <= hi)
        right = geom.usable & (geom.beam_angle >= -hi) & (geom.beam_angle <= -lo)
        if delta > 0.0 and left.any() and near[left].min() < p.side_clearance:
            delta, res.reason = 0.0, 'left side too close'
        elif delta < 0.0 and right.any() and near[right].min() < p.side_clearance:
            delta, res.reason = 0.0, 'right side too close'
    delta = max(-p.max_steer, min(p.max_steer, delta))

    # 7. speed
    a = abs(math.degrees(delta))
    v = p.speeds[-1]
    for limit, speed in zip(p.speed_angles_deg, p.speeds):
        if a < limit:
            v = speed
            break

    res.ok = True
    res.steering = float(delta)
    res.speed = float(min(v, p.v_max))
    return res
