# PR01 — ROS 2 graph

## Environment

ROS distribution: Jazzy

Normal domain:
ROS_DOMAIN_ID=16

Broken domain:
ROS_DOMAIN_ID=17

## Normal graph

Commands:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
Nodes:
- /turtlesim — turtlesim simulator
- /teleop_turtle — keyboard control node
Main topics:
- /turtle1/cmd_vel — geometry_msgs/msg/Twist
- /turtle1/pose — turtlesim/msg/Pose
- /turtle1/color_sensor — turtlesim/msg/Color
- /parameter_events — rcl_interfaces/msg/ParameterEvent
- /rosout — rcl_interfaces/msg/Log
The /turtle1/pose topic continuously publishes the turtle position.
Measured pose frequency:
TODO 62.5 Hz, measured for TODO 0.018 s.
Domain failure
Simulator remained running with:
ROS_DOMAIN_ID=16
The teleop node and observation CLI were restarted with:
ROS_DOMAIN_ID=17
Observed graph in domain 17:
- /teleop_turtle was visible
- /turtlesim was not visible
- /turtle1/pose data was not received
- timeout exit code: 124
The turtle could not be controlled from the teleop node.
Recovery
The teleop node and CLI were restarted with:
ROS_DOMAIN_ID=16
After returning to the original domain:
- /turtlesim became visible
- /teleop_turtle became visible
- /turtle1/pose produced data
- timeout exit code: 0
- keyboard control worked again
Explanation
ROS_DOMAIN_ID defines the discovery domain used by ROS 2 participants.
Nodes in different ROS domains do not discover each other.
Changing the ROS_DOMAIN_ID environment variable does not change the domain
of an already running ROS node. Therefore the teleop node had to be stopped
and started again after changing ROS_DOMAIN_ID.
