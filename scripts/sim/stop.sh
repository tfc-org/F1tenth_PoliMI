#!/bin/bash
# Stop the simulator and the container: stop.sh [--volumes]
#   --volumes  also delete the build/install/log volumes (next start rebuilds the whole workspace)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/.utils/common.sh"

case "${1:-}" in
    "") docker compose down ;;
    --volumes) docker compose down -v ;;
    *) echo "usage: stop.sh [--volumes]" >&2; exit 2 ;;
esac
