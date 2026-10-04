"""ROS 2 node: /scan -> Follow the Gap -> /drive, with debug markers.

Parameters are live: `ros2 param set /gap_follow ftg.v_max 1.0` applies on the next scan
(topic names and base_frame need a restart).
"""
from dataclasses import fields
import math

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Point
import numpy as np
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray

from .ftg import FtgParams, follow_the_gap
from .scan_utils import LidarConfig, Mount, ScanGeometry

MAX_MARKER_POINTS = 400


def _ros_default(v):
    return [float(x) for x in v] if isinstance(v, tuple) else v


def _from_params(cls, node, prefix, pending=None):
    """Build a config dataclass from the node's parameters, with `pending` {name: value} on top."""
    pending = pending or {}
    kwargs = {}
    for f in fields(cls):
        name = f'{prefix}.{f.name}'
        v = pending[name] if name in pending else node.get_parameter(name).value
        kwargs[f.name] = tuple(v) if isinstance(f.default, tuple) else v
    return cls(**kwargs)


def _build(node, pending=None):
    """Validated (LidarConfig, FtgParams); raises ValueError / TypeError."""
    lidar = _from_params(LidarConfig, node, 'lidar', pending)
    lidar.mask_pairs_rad()
    ftg = _from_params(FtgParams, node, 'ftg', pending)
    ftg.validate()
    return lidar, ftg


class GapFollowNode(Node):

    def __init__(self):
        super().__init__('gap_follow')
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('drive_topic', '/drive')
        self.declare_parameter('marker_topic', '/ftg/markers')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('enabled', True)
        self.declare_parameter('steer_tau', 0.05)       # s, steering low-pass; 0 disables
        self.declare_parameter('marker_rate', 10.0)     # Hz; 0 disables markers
        self.declare_parameter('tf_timeout', 2.0)       # s, then assume laser at base_frame origin
        for f in fields(LidarConfig):
            self.declare_parameter(f'lidar.{f.name}', _ros_default(f.default))
        for f in fields(FtgParams):
            self.declare_parameter(f'ftg.{f.name}', _ros_default(f.default))

        self.lidar = LidarConfig()
        self.ftg = FtgParams()
        self.geom = ScanGeometry(self.lidar)
        self._load_params()
        self._dirty = False
        self.add_on_set_parameters_callback(self._on_set_params)

        self.base_frame = self.get_parameter('base_frame').value
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self._mount_frame = None
        self._tf_wait_start = None

        self._steer = 0.0
        self._last_stamp = None
        self._last_markers = None
        self._stop_sent = False

        qos = QoSProfile(depth=1, history=HistoryPolicy.KEEP_LAST, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, self.get_parameter('drive_topic').value, 10)
        self.marker_pub = self.create_publisher(MarkerArray, self.get_parameter('marker_topic').value, 1)
        self.create_subscription(LaserScan, self.get_parameter('scan_topic').value, self._on_scan, qos)
        self.get_logger().info(
            f'gap_follow: {self.get_parameter("scan_topic").value} -> {self.get_parameter("drive_topic").value}, '
            f'base_frame={self.base_frame}, v_max={self.ftg.v_max} m/s')

    # ---------- parameters ----------

    def _on_set_params(self, params):
        # Reject bad values here, so `ros2 param set` reports the error instead of storing it.
        try:
            _build(self, {p.name: p.value for p in params})
        except (ValueError, TypeError) as e:
            return SetParametersResult(successful=False, reason=str(e))
        self._dirty = True
        return SetParametersResult(successful=True)

    def _load_params(self):
        try:
            lidar, ftg = _build(self)
        except (ValueError, TypeError) as e:
            self.get_logger().error(f'invalid parameters, keeping the previous ones: {e}')
            return
        self.lidar, self.ftg = lidar, ftg
        self.geom.set_config(lidar)

    # ---------- main loop ----------

    def _on_scan(self, msg: LaserScan):
        if self._dirty:
            self._dirty = False
            self._load_params()

        if not self.get_parameter('enabled').value:
            if not self._stop_sent:
                self.publish_stop()
                self.get_logger().info('disabled: stop sent, not publishing')
            return
        self._stop_sent = False

        if not self._ensure_mount(msg.header.frame_id):
            return
        if self.geom.update(len(msg.ranges), msg.angle_min, msg.angle_increment):
            self.get_logger().info(
                f'scan layout: {self.geom.n} beams, {math.degrees(self.geom.increment):.3f} deg/beam, '
                f'{int(self.geom.in_fov.sum())} in the FOV window')
            if self.geom.increment_mismatch():
                self.get_logger().warn(
                    f'angle_increment {math.degrees(self.geom.increment):.3f} deg differs from '
                    f'lidar.expected_increment_deg {self.lidar.expected_increment_deg}')

        r = self.geom.clean(msg.ranges)
        res = follow_the_gap(r, self.geom, self.ftg)

        if res.ok:
            steer = self._filter(res.steering, Time.from_msg(msg.header.stamp).nanoseconds * 1e-9)
            speed = res.speed
            if res.reason:
                self.get_logger().info(res.reason, throttle_duration_sec=2.0)
        else:
            steer, speed = 0.0, 0.0
            self._steer, self._last_stamp = 0.0, None
            self.get_logger().warn(f'stopping: {res.reason}', throttle_duration_sec=1.0)
        self._publish_drive(steer, speed)
        self._maybe_publish_markers(msg, r, res, steer, speed)

    def _filter(self, target, t):
        tau = float(self.get_parameter('steer_tau').value)
        dt = None if self._last_stamp is None else t - self._last_stamp
        self._last_stamp = t
        if tau <= 0.0 or dt is None or dt <= 0.0 or dt > 0.5:
            self._steer = target
        else:
            self._steer += dt / (tau + dt) * (target - self._steer)
        return self._steer

    def _ensure_mount(self, frame):
        if frame == self._mount_frame:
            return True
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, frame, Time())
        except TransformException as e:
            now = self.get_clock().now()
            if self._tf_wait_start is None:
                self._tf_wait_start = now
            waited = (now - self._tf_wait_start).nanoseconds * 1e-9
            if waited < float(self.get_parameter('tf_timeout').value):
                self.get_logger().info(f'waiting for TF {self.base_frame} <- {frame}', throttle_duration_sec=1.0)
                return False
            self.get_logger().warn(
                f'no TF {self.base_frame} <- {frame} after {waited:.1f} s ({e}). '
                'Assuming the laser sits at the base_frame origin, facing forward.')
            mount = Mount()
        else:
            tr, q = tf.transform.translation, tf.transform.rotation
            mount = Mount.from_tf(tr.x, tr.y, tr.z, q.x, q.y, q.z, q.w)
            self.get_logger().info(f'laser mount from TF ({self.base_frame} <- {frame}): {mount.describe()}')
        self.geom.set_mount(mount)
        self._mount_frame = frame
        self._tf_wait_start = None
        return True

    # ---------- output ----------

    def _publish_drive(self, steer, speed):
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.base_frame
        msg.drive.steering_angle = float(steer)
        msg.drive.speed = float(speed)
        self.drive_pub.publish(msg)

    def publish_stop(self):
        self._publish_drive(0.0, 0.0)
        self._stop_sent = True

    def _maybe_publish_markers(self, scan, r, res, steer, speed):
        rate = float(self.get_parameter('marker_rate').value)
        if rate <= 0.0:
            return
        now = self.get_clock().now()
        if self._last_markers is not None and (now - self._last_markers).nanoseconds < 1e9 / rate:
            return
        self._last_markers = now

        near = np.minimum(r, self.ftg.r_max)
        x, y = self.geom.points(near)
        stamp, frame = scan.header.stamp, self.base_frame
        lifetime = Duration(seconds=0.5).to_msg()

        def marker(mid, mtype, rgb, scale):
            m = Marker()
            m.header.stamp, m.header.frame_id = stamp, frame
            m.ns, m.id, m.type, m.action = 'ftg', mid, mtype, Marker.ADD
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = m.scale.z = scale
            m.color.r, m.color.g, m.color.b, m.color.a = (*rgb, 1.0)
            m.lifetime = lifetime
            return m

        def points(m, idx):
            idx = np.asarray(idx)
            step = max(1, len(idx) // MAX_MARKER_POINTS)
            m.points = [Point(x=float(x[k]), y=float(y[k]), z=0.05) for k in idx[::step]]
            return m

        out = MarkerArray()
        out.markers.append(points(marker(0, Marker.POINTS, (1.0, 0.2, 0.2), 0.06), np.flatnonzero(res.bubble)))
        s, e = res.gap
        out.markers.append(points(marker(1, Marker.POINTS, (0.2, 0.9, 0.3), 0.04), np.arange(s, e)))
        target = marker(2, Marker.SPHERE, (0.2, 0.5, 1.0), 0.2)
        target.pose.position.x, target.pose.position.y, target.pose.position.z = (*res.target_xy, 0.1)
        if not res.ok:
            target.action = Marker.DELETE
        out.markers.append(target)
        arrow = marker(3, Marker.ARROW, (1.0, 0.85, 0.1), 0.05)
        arrow.scale.y, arrow.scale.z = 0.1, 0.1
        length = 0.3 + 0.4 * speed
        arrow.points = [Point(x=0.0, y=0.0, z=0.1),
                        Point(x=length * math.cos(steer), y=length * math.sin(steer), z=0.1)]
        out.markers.append(arrow)
        self.marker_pub.publish(out)


def main(args=None):
    # Handle Ctrl-C ourselves so the context is still valid to send a final stop,
    # without waiting for the mux timeout.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = GapFollowNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.publish_stop()
            node.get_logger().info('stop sent, shutting down')
        except Exception:  # noqa: BLE001 - best effort on the way out
            pass
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
