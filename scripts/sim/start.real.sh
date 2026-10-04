#!/bin/bash
# The simulator as the car, with all its imperfections: start.real.sh [map] [launch args...]
set -euo pipefail

exec bash "$(dirname "$0")/.utils/start_mask.sh" "$@"
