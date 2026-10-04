"""Follow the Gap node.

Sim (simcar) and car:  ros2 launch polimi_reactive gap_follow.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('polimi_reactive')
    args = [
        DeclareLaunchArgument(
            'params', default_value=os.path.join(share, 'config', 'ftg.yaml'),
            description='Follow the Gap parameters and how the controller uses the scan.'),
        DeclareLaunchArgument(
            'base_frame', default_value='base_link',
            description='Car frame: base_link on the car and in simcar.'),
        DeclareLaunchArgument('scan_topic', default_value='/scan'),
        DeclareLaunchArgument('drive_topic', default_value='/drive'),
    ]
    node = Node(
        package='polimi_reactive',
        executable='gap_follow',
        name='gap_follow',
        output='screen',
        emulate_tty=True,
        parameters=[
            LaunchConfiguration('params'),
            {
                'base_frame': LaunchConfiguration('base_frame'),
                'scan_topic': LaunchConfiguration('scan_topic'),
                'drive_topic': LaunchConfiguration('drive_topic'),
            },
        ],
    )
    return LaunchDescription(args + [node])
