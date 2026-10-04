#!/bin/bash
# Keyboard control of the simulated car. Run it in a second terminal while the simulator is up.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/.utils/common.sh"

require_sim
cat <<'KEYS'
Hold a key: the car stops 0.2-0.5 s after the last one (mux and VESC timeouts).
  i forward    , reverse    u / o forward-left / right    k stop
  q / z speed +-10% (starts at 0.5 m/s)    Ctrl-C quit    no arrow keys
KEYS
in_container "ros2 run teleop_twist_keyboard teleop_twist_keyboard"
