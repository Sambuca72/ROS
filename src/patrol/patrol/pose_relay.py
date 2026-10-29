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

"""Republish turtle poses with best-effort reliability."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseRelay(Node):
    """Relay a reliable turtlesim input to a best-effort sensor topic."""

    def __init__(self):
        """Create relative input and output topics for launch remapping."""
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        self.subscription = self.create_subscription(
            Pose, 'pose', self.on_pose, 10)

    def on_pose(self, pose):
        """Forward each pose without changing its values."""
        self.publisher.publish(pose)


def main(args=None):
    """Run the node and release its ROS context on shutdown."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseRelay()
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
