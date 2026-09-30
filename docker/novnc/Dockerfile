# Virtual X display + browser-based viewer (noVNC) for the ROS containers.
# ROS containers draw on DISPLAY=:1 via a shared X11 socket volume;
# you watch it at http://localhost:8080 (see docker-compose.yaml).
# Multi-arch: builds on Apple Silicon, x86 and Jetson.
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb x11vnc fluxbox novnc websockify x11-utils \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
