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

"""Validate motion settings without initializing ROS."""

from patrol.settings import Settings, updated_settings
import pytest


@pytest.mark.parametrize('changes', [
    {'linear_speed': 0.0, 'turn_rate': -1.0, 'publish_hz': 1.0},
    {'linear_speed': 1.0, 'turn_rate': 1.0, 'publish_hz': 30.0},
    {'publish_hz': 5.0},
])
def test_valid_settings(changes):
    """Accept inclusive boundaries and the required 10 to 5 Hz change."""
    current = Settings()
    candidate = updated_settings(current, changes)
    for name, value in changes.items():
        assert getattr(candidate, name) == value
    assert current == Settings()


@pytest.mark.parametrize('name,value', [
    ('publish_hz', 0.0), ('publish_hz', -1.0),
    ('publish_hz', 0.99), ('publish_hz', 30.01),
    ('linear_speed', -0.01), ('linear_speed', 1.01),
    ('turn_rate', -1.01), ('turn_rate', 1.01),
    ('publish_hz', True), ('publish_hz', '5.0'),
])
def test_invalid_settings(name, value):
    """Reject invalid inputs before changing the current settings."""
    current = Settings()
    with pytest.raises(ValueError, match=name):
        updated_settings(current, {name: value})
    assert current == Settings()


@pytest.mark.parametrize('name', ['linear_speed', 'turn_rate', 'publish_hz'])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_settings(name, value):
    """Reject NaN and both infinities for every motion parameter."""
    with pytest.raises(ValueError, match=name):
        updated_settings(Settings(), {name: value})


def test_unknown_parameter():
    """Do not silently accept a misspelled setting."""
    with pytest.raises(ValueError, match='Unknown'):
        updated_settings(Settings(), {'publsh_hz': 5.0})
