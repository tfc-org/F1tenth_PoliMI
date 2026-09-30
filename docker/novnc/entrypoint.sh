#!/bin/bash
# Xvfb (display :1, unix socket only) -> fluxbox -> x11vnc (localhost only) -> noVNC on :8080
set -e
RESOLUTION=${RESOLUTION:-1920x1080x24}

# Shared socket dir must be world-writable (sticky) so the ROS user can connect.
mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

Xvfb :1 -screen 0 "$RESOLUTION" -nolisten tcp -ac +extension GLX +render -noreset &
export DISPLAY=:1
for i in $(seq 50); do xdpyinfo >/dev/null 2>&1 && break; sleep 0.1; done

fluxbox >/dev/null 2>&1 &

VNC_AUTH="-nopw"
if [ -n "$VNC_PASSWORD" ]; then
    x11vnc -storepasswd "$VNC_PASSWORD" /tmp/vncpass >/dev/null
    VNC_AUTH="-rfbauth /tmp/vncpass"
fi
x11vnc -display :1 -forever -shared -localhost -rfbport 5900 -quiet $VNC_AUTH &

websockify --web /usr/share/novnc 8080 localhost:5900 &

echo "noVNC ready: open http://localhost:8080 (resolution $RESOLUTION)"
# Exit if any process dies, so docker restarts the container.
wait -n
