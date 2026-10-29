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

"""Observe the sensor stream with a configurable reliability policy."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    """Count delivered poses and log the first successful delivery."""

    def __init__(self):
        """Select reliability at startup so the QoS mismatch is repeatable."""
        super().__init__('pose_subscriber')
        self.declare_parameter('reliability', 'best_effort')
        reliability = self.get_parameter('reliability').value
        policies = {
            'reliable': ReliabilityPolicy.RELIABLE,
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
        }
        if reliability not in policies:
            raise ValueError('reliability must be reliable or best_effort')
        self.received_count = 0
        qos = QoSProfile(depth=10, reliability=policies[reliability])
        self.subscription = self.create_subscription(
            Pose, 'sensor_pose', self.on_pose, qos)
        self.get_logger().info(f'Subscribing to sensor_pose: {reliability}')

    def on_pose(self, pose):
        """Count actual callbacks instead of assuming discovery means delivery."""
        self.received_count += 1
        if self.received_count == 1:
            self.get_logger().info(
                f'First sensor_pose received: x={pose.x:.3f}, y={pose.y:.3f}')


def main(args=None):
    """Run the node and release its ROS context on shutdown."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseSubscriber()
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
