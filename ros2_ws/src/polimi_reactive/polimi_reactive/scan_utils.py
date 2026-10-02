"""LiDAR geometry and preprocessing shared by the reactive nodes.

Beam angles always come from the LaserScan message (angle_min + i * angle_increment),
never from hard-coded indices. The LiDAR mount (position, yaw, upside-down) comes from
TF (base_frame <- scan frame), so the same code runs on the sim and on the car.
All angles exposed here are in the base frame: 0 = straight ahead, positive = left.
"""
from dataclasses import dataclass, field
import math

import numpy as np


def wrap(a):
    """Wrap angles to [-pi, pi)."""
    return (np.asarray(a) + np.pi) % (2.0 * np.pi) - np.pi


@dataclass
class LidarConfig:
    """How the controller uses the scan. Not the sensor's own settings (those are in the message)."""

    fov_min_deg: float = -90.0          # usable window, base frame
    fov_max_deg: float = 90.0
    mask_deg: tuple = (0.0, 0.0)        # blocked sectors as flat pairs [lo1, hi1, ...]; pairs with lo >= hi are ignored
    range_min: float = 0.05             # closer readings are self-hits / dust: treated as "no return"
    range_max: float = 15.0             # farther readings are not trusted: clipped to this
    expected_increment_deg: float = 0.0  # sanity check only; 0 disables it

    def mask_pairs_rad(self):
        m = [float(v) for v in self.mask_deg]
        if len(m) % 2:
            raise ValueError('lidar.mask_deg needs pairs [lo, hi, ...]')
        return [(math.radians(lo), math.radians(hi)) for lo, hi in zip(m[0::2], m[1::2]) if lo < hi]


@dataclass
class Mount:
    """Pose of the laser frame in the base frame: p_base = R @ p_laser + t."""

    t: np.ndarray = field(default_factory=lambda: np.zeros(3))
    R: np.ndarray = field(default_factory=lambda: np.eye(3))

    @staticmethod
    def from_tf(tx, ty, tz, qx, qy, qz, qw):
        n = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw) or 1.0
        x, y, z, w = qx / n, qy / n, qz / n, qw / n
        R = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ])
        return Mount(np.array([tx, ty, tz], dtype=float), R)

    @staticmethod
    def planar(x=0.0, y=0.0, yaw=0.0, inverted=False):
        """Convenience for tests: yaw about z, optionally upside down (roll = pi)."""
        c, s = math.cos(yaw), math.sin(yaw)
        Rz = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        Rx = np.diag([1.0, -1.0, -1.0]) if inverted else np.eye(3)
        return Mount(np.array([x, y, 0.0]), Rz @ Rx)

    def describe(self):
        yaw = math.degrees(math.atan2(self.R[1, 0], self.R[0, 0]))
        inverted = self.R[2, 2] < 0
        return f'x={self.t[0]:.3f} y={self.t[1]:.3f} yaw={yaw:.1f}deg{" (upside down)" if inverted else ""}'


class ScanGeometry:
    """Per-beam directions in the base frame, rebuilt only when the scan layout or the mount changes."""

    def __init__(self, cfg: LidarConfig, mount: Mount = None):
        self.cfg = cfg
        self.mount = mount or Mount()
        self._key = None
        self.n = 0
        self.increment = 0.0
        self.beam_angle = np.zeros(0)
        self.dx = np.zeros(0)
        self.dy = np.zeros(0)
        self.usable = np.zeros(0, bool)
        self.in_fov = np.zeros(0, bool)

    def set_config(self, cfg: LidarConfig):
        self.cfg = cfg
        self._key = None

    def set_mount(self, mount: Mount):
        self.mount = mount
        self._key = None

    def update(self, n, angle_min, angle_increment):
        """Rebuild the tables if the layout changed. Returns True when rebuilt."""
        key = (int(n), float(angle_min), float(angle_increment))
        if key == self._key:
            return False
        theta = angle_min + np.arange(n) * angle_increment
        d_laser = np.stack([np.cos(theta), np.sin(theta), np.zeros(n)])
        d_base = self.mount.R @ d_laser
        self.dx, self.dy = d_base[0], d_base[1]
        self.beam_angle = np.arctan2(self.dy, self.dx)
        usable = np.ones(n, bool)
        for lo, hi in self.cfg.mask_pairs_rad():
            usable &= ~((self.beam_angle >= lo) & (self.beam_angle <= hi))
        lo, hi = math.radians(self.cfg.fov_min_deg), math.radians(self.cfg.fov_max_deg)
        self.usable = usable
        self.in_fov = usable & (self.beam_angle >= lo) & (self.beam_angle <= hi)
        self.n = int(n)
        self.increment = abs(float(angle_increment))
        self._key = key
        return True

    def increment_mismatch(self):
        exp = self.cfg.expected_increment_deg
        return exp > 0.0 and abs(math.degrees(self.increment) - exp) > 0.05 * exp

    def clean(self, ranges):
        """NaN / inf / too close / too far -> range_max ("no return"), then clip to range_max."""
        r = np.asarray(ranges, dtype=float)
        bad = ~np.isfinite(r) | (r < self.cfg.range_min)
        r = np.where(bad, self.cfg.range_max, r)
        return np.minimum(r, self.cfg.range_max)

    def points(self, r, idx=slice(None)):
        """Hit points in the base frame for ranges r (same length as the scan, or matching idx)."""
        x = self.mount.t[0] + r * self.dx[idx]
        y = self.mount.t[1] + r * self.dy[idx]
        return x, y
