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

"""Verify QoS incompatibility and recovery using actual DDS delivery."""

import time

from patrol.pose_relay import PoseRelay
from patrol.pose_subscriber import PoseSubscriber
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


@pytest.mark.parametrize('reliability', ['reliable', 'best_effort'])
def test_sensor_delivery_depends_on_subscriber_qos(reliability):
    """Prove the relay is active even when the requested QoS blocks delivery."""
    rclpy.init(args=[
        '--ros-args', '-r', '__ns:=/pr05_test',
        '-p', f'reliability:={reliability}',
    ])
    nodes = []
    executor = SingleThreadedExecutor()
    try:
        source = Node('pose_source')
        nodes.append(source)
        relay = PoseRelay()
        nodes.append(relay)
        subscriber = PoseSubscriber()
        nodes.append(subscriber)
        publisher = source.create_publisher(Pose, 'pose', 10)
        observed = []
        sensor_qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        observer = source.create_subscription(
            Pose, 'sensor_pose', observed.append, sensor_qos)
        for node in nodes:
            executor.add_node(node)
        pose = Pose(x=2.0, y=3.0, theta=0.25,
                    linear_velocity=0.5, angular_velocity=0.125)
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            publisher.publish(pose)
            executor.spin_once(timeout_sec=0.02)
        assert observed, 'The independent best-effort observer got no poses'
        assert all(message == pose for message in observed)
        if reliability == 'reliable':
            assert subscriber.received_count == 0
        else:
            assert subscriber.received_count > 0
        source.destroy_subscription(observer)
    finally:
        executor.shutdown()
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.shutdown()
