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

"""Launch one turtle, namespaced patrol nodes and an optional MCAP recorder."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    """Keep launch settings deferred until their runtime values are known."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    reliability = LaunchConfiguration('subscriber_reliability')
    sensor_topic = PathJoinSubstitution(['/', namespace, 'sensor_pose'])

    arguments = [
        DeclareLaunchArgument('namespace', default_value='robot_a',
                              description='Namespace for the patrol and sensor nodes'),
        DeclareLaunchArgument('record', default_value='false',
                              choices=['true', 'false'],
                              description='Start the MCAP recorder when true'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag',
                              description='New output directory for the recording'),
        DeclareLaunchArgument('subscriber_reliability', default_value='best_effort',
                              choices=['reliable', 'best_effort'],
                              description='Reliability requested by the sensor subscriber'),
    ]
    nodes = [
        Node(package='turtlesim', executable='turtlesim_node',
             namespace='/', output='screen'),
        Node(package='patrol', executable='patrol', namespace=namespace,
             output='screen', remappings=[
                 ('turtle1/pose', '/turtle1/pose'),
                 ('cmd_vel', '/turtle1/cmd_vel'),
             ]),
        Node(package='patrol', executable='pose_relay', namespace=namespace,
             output='screen', remappings=[('pose', '/turtle1/pose')]),
        Node(package='patrol', executable='pose_subscriber', namespace=namespace,
             output='screen', parameters=[{'reliability': reliability}]),
    ]
    recorder = ExecuteProcess(
        cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
             '--topics', sensor_topic],
        condition=IfCondition(record), output='screen',
    )
    return LaunchDescription(arguments + [
        LogInfo(msg=['Patrol namespace: ', namespace,
                     '; subscriber reliability: ', reliability]),
        LogInfo(msg=['MCAP recording: ', record, '; directory: ', bag_dir]),
    ] + nodes + [recorder])
