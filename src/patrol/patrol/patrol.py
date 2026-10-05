# Copyright 2026 Sambuca72
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Receive the turtle pose and publish a command every 0.1 seconds."""

from geometry_msgs.msg import Twist
from patrol.command import command_for_pose
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim.msg import Pose


class Patrol(Node):
    """Keep the most recent pose and send commands from a timer."""

    def __init__(self):
        """Create the subscriber, publisher, and timer."""
        super().__init__('patrol')
        self.last_pose = None
        self.pose_subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.command_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.command_timer = self.create_timer(0.1, self.on_timer)

    def on_pose(self, pose):
        """Save the latest pose without choosing or publishing commands."""
        self.last_pose = pose

    def on_timer(self):
        """Publish zero before the first pose, then the patrol command."""
        self.command_publisher.publish(command_for_pose(self.last_pose))


def main(args=None):
    """Initialize ROS, run callbacks, and clean up on Ctrl+C."""
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
