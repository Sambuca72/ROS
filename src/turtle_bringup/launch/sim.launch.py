"""Launch one turtlesim node for practice PR02."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Describe the process started and stopped by ros2 launch."""
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen',
        ),
    ])
