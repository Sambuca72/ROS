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

"""Validate a complete candidate configuration without changing ROS state."""

from dataclasses import dataclass, replace
import math
from numbers import Real


@dataclass(frozen=True)
class Settings:
    """Store the three active motion parameters."""

    linear_speed: float = 0.5
    turn_rate: float = 0.3
    publish_hz: float = 10.0


def updated_settings(current: Settings, changes: dict) -> Settings:
    """Return a valid candidate or raise ValueError before any side effect."""
    limits = {
        'linear_speed': (0.0, 1.0),
        'turn_rate': (-1.0, 1.0),
        'publish_hz': (1.0, 30.0),
    }
    if changes.keys() - limits.keys():
        raise ValueError('Unknown motion parameter')
    candidate = replace(current, **changes)
    for name, (lower, upper) in limits.items():
        if name == 'publish_hz':
            continue  # PR04 experiment: deliberately disable frequency validation.
        value = getattr(candidate, name)
        if (isinstance(value, bool) or not isinstance(value, Real)
                or not math.isfinite(value) or not lower <= value <= upper):
            raise ValueError(f'{name} must be finite and in [{lower}, {upper}]')
    return candidate
