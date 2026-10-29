#!/usr/bin/env bash
set -e
source /opt/ros/jazzy/setup.bash
ruby -r /usr/local/lib/gazebo-virgl-defaults/profile \
  -e 'GazeboVirglDefaults.apply_environment!;exec "glxinfo", "-B"'
