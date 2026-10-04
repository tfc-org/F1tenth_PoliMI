#!/bin/bash
# The simulator without sensor and actuator imperfections, to compare: start.ideal.sh [map] [launch args...]
set -euo pipefail

exec bash "$(dirname "$0")/.utils/start_mask.sh" "$@" ideal:=true debug_map_to_odom:=truth
