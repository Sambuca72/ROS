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

"""Exercise the installed launch, namespacing, recording and clean shutdown."""

import os
import signal
import subprocess
import time

import pytest
import yaml


@pytest.mark.parametrize('record', [False, True])
def test_installed_launch_recording_and_shutdown(tmp_path, record):
    """Run all nodes and verify the runtime condition and namespaced bag topic."""
    namespace = 'pr05_launch_record' if record else 'pr05_launch_no_record'
    bag = tmp_path / 'bag'
    log_path = tmp_path / 'launch.log'
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen',
               ROS_LOG_DIR=str(tmp_path / 'ros-logs'))
    command = [
        'ros2', 'launch', 'course_bringup', 'patrol.launch.py',
        f'namespace:={namespace}', f'record:={str(record).lower()}',
        f'bag_dir:={bag}', 'subscriber_reliability:=best_effort',
    ]
    with log_path.open('w') as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT,
            env=env, start_new_session=True)
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                output = log_path.read_text()
                received = 'First sensor_pose received:' in output
                recorder_ready = 'All requested topics are subscribed' in output
                if received and (not record or recorder_ready):
                    time.sleep(0.3)
                    break
                assert process.poll() is None, output
                time.sleep(0.05)
            else:
                pytest.fail('Launch did not become ready:\n' + log_path.read_text())
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=12)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=3)
                    pytest.fail('Launch did not shut down after SIGINT')
    output = log_path.read_text()
    assert process.returncode == 0, output
    assert 'Traceback' not in output and '[ERROR]' not in output, output
    assert f'[{namespace}.pose_subscriber]' in output
    assert 'First sensor_pose received:' in output
    assert bag.exists() is record
    if record:
        metadata = yaml.safe_load((bag / 'metadata.yaml').read_text())
        info = metadata['rosbag2_bagfile_information']
        assert info['storage_identifier'] == 'mcap'
        assert info['message_count'] > 0
        topics = info['topics_with_message_count']
        assert len(topics) == 1
        assert topics[0]['topic_metadata']['name'] == f'/{namespace}/sensor_pose'
    else:
        assert 'rosbag2_recorder' not in output
