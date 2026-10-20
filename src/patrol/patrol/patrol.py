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

"""Receive turtle poses and publish dynamically configured motion commands."""

from geometry_msgs.msg import Twist
from patrol.command import command_for_pose
from patrol.settings import Settings, updated_settings
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim.msg import Pose


class Patrol(Node):
    """Keep the most recent pose and validate live motion parameter changes."""

    def __init__(self):
        """Create the subscriber, publisher, and timer."""
        super().__init__('patrol')
        defaults = Settings()
        for name in ('linear_speed', 'turn_rate', 'publish_hz'):
            self.declare_parameter(name, getattr(defaults, name))
        self.settings = updated_settings(defaults, {
            name: self.get_parameter(name).value
            for name in ('linear_speed', 'turn_rate', 'publish_hz')
        })
        self.last_pose = None
        self.pose_subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.command_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.command_timer = self.create_timer(
            1.0 / self.settings.publish_hz, self.on_timer)
        self.add_on_set_parameters_callback(self.validate_parameters)
        self.add_post_set_parameters_callback(self.apply_parameters)

    def candidate_settings(self, parameters):
        """Merge motion parameters into a validated immutable candidate."""
        names = ('linear_speed', 'turn_rate', 'publish_hz')
        return updated_settings(self.settings, {
            parameter.name: parameter.value for parameter in parameters
            if parameter.name in names
        })

    def validate_parameters(self, parameters):
        """Reject invalid updates without touching active settings or timers."""
        try:
            self.candidate_settings(parameters)
        except ValueError as error:
            return SetParametersResult(successful=False, reason=str(error))
        return SetParametersResult(successful=True)

    def apply_parameters(self, parameters):
        """Apply accepted values after every validation callback has passed."""
        candidate = self.candidate_settings(parameters)
        if candidate.publish_hz != self.settings.publish_hz:
            old_timer = self.command_timer
            old_timer.cancel()
            self.command_timer = self.create_timer(
                1.0 / candidate.publish_hz, self.on_timer)
            self.destroy_timer(old_timer)
        self.settings = candidate

    def on_pose(self, pose):
        """Save the latest pose without choosing or publishing commands."""
        self.last_pose = pose

    def on_timer(self):
        """Publish zero before the first pose, then the patrol command."""
        self.command_publisher.publish(command_for_pose(self.last_pose, self.settings))


def main(args=None):
    """Initialize ROS, run callbacks, and clean up on Ctrl+C."""
    rclpy.init(args=args)
    node = None
    try:
        node = Patrol()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
