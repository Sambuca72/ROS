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

"""Check real rclpy parameter transactions and timer ownership."""

from patrol.patrol import Patrol
from patrol.settings import Settings
import pytest
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.parameter import Parameter


@pytest.fixture
def node():
    """Create a patrol node and clean up its ROS context after each test."""
    rclpy.init(args=[])
    instance = Patrol()
    try:
        yield instance
    finally:
        instance.destroy_node()
        rclpy.shutdown()


def test_valid_frequency_replaces_one_timer(node):
    """Replace the old timer with exactly one timer at 5 Hz."""
    old_timer = node.command_timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=5.0)])
    assert result.successful
    assert node.get_parameter('publish_hz').value == 5.0
    assert node.settings.publish_hz == 5.0
    assert node.command_timer.timer_period_ns == 200_000_000
    assert list(node.timers) == [node.command_timer]
    assert old_timer is not node.command_timer


@pytest.mark.parametrize('value', [0.0, -1.0, float('nan'), float('inf'), 31.0])
def test_invalid_frequency_preserves_state(node, value):
    """Run the same rejection test on both broken and fixed revisions."""
    timer = node.command_timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=value)])
    assert not result.successful
    assert 'publish_hz' in result.reason
    assert node.get_parameter('publish_hz').value == 10.0
    assert node.settings == Settings()
    assert node.command_timer is timer
    assert not timer.is_canceled()
    assert timer.timer_period_ns == 100_000_000
    assert list(node.timers) == [timer]


def test_mixed_invalid_update_is_atomic(node):
    """Do not apply a valid speed if the same transaction has an invalid rate."""
    timer = node.command_timer
    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('publish_hz', value=0.0),
    ])
    assert not result.successful
    assert node.settings == Settings()
    assert node.get_parameter('linear_speed').value == 0.5
    assert node.command_timer is timer


def test_later_validator_rejection_has_no_side_effects(node):
    """A callback rejecting after ours must leave the timer untouched."""
    node.add_on_set_parameters_callback(
        lambda parameters: SetParametersResult(successful=False, reason='test veto'))
    node.remove_on_set_parameters_callback(node.validate_parameters)
    node.add_on_set_parameters_callback(node.validate_parameters)
    timer = node.command_timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=5.0)])
    assert not result.successful
    assert node.settings == Settings()
    assert node.get_parameter('publish_hz').value == 10.0
    assert node.command_timer is timer
    assert not timer.is_canceled()


def test_speed_update_and_same_frequency_keep_timer(node):
    """Update speed and turn without replacing an unchanged 10 Hz timer."""
    timer = node.command_timer
    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('turn_rate', value=-0.4),
        Parameter('publish_hz', value=10.0),
    ])
    assert result.successful
    assert node.settings == Settings(0.8, -0.4, 10.0)
    assert node.command_timer is timer


def test_invalid_startup_override():
    """Reject an invalid startup rate before creating a motion timer."""
    rclpy.init(args=['--ros-args', '-p', 'publish_hz:=0.0'])
    try:
        with pytest.raises(ValueError, match='publish_hz'):
            Patrol()
    finally:
        rclpy.shutdown()
