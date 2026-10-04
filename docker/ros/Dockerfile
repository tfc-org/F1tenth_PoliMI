# F1tenth_PoliMI dev / car image. Built by docker-compose.yaml (build context = repo root).
#
# One image for all targets:
#   arm, x86  WITH_SIM=1  -> + f1tenth_gym (pip) and f1tenth_gym_ros (built in /opt/sim_ws)
#   jet       WITH_SIM=0  -> drivers and autonomy only, no simulator on the car
#
# ros2_ws/src is bind-mounted at run time; it is copied here only so rosdep can
# read the package.xml files. Rebuild the image when a package.xml changes.
ARG BASE_IMAGE=ros:humble
FROM ${BASE_IMAGE}

ARG USER
ARG UID
ARG GID
ARG WITH_SIM=1
# Pinned upstream commits (dev-humble). Bump on purpose, never follow the branch.
ARG GYM_REF=bdaec1420c3b0f103858d289866d0d4e2e597c30
ARG GYM_ROS_REF=08395766c4d9dc5a763381f1dd6fa4a3d68df66e
# f1tenth_stack depends on drivers we don't use (Hokuyo, SICK, rosbridge).
ARG ROSDEP_SKIP="urg_node sick_scan_xd rosbridge_server"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo git tmux nano less wget jq net-tools joystick \
        python3-pip python3-colcon-common-extensions python3-colcon-clean \
        libasio-dev \
        ros-humble-rmw-zenoh-cpp \
        ros-humble-ackermann-msgs \
        ros-humble-asio-cmake-module \
        ros-humble-tf-transformations \
        ros-humble-tf2-tools \
        ros-humble-xacro \
        ros-humble-robot-state-publisher \
        ros-humble-slam-toolbox \
        ros-humble-nav2-map-server \
        ros-humble-nav2-lifecycle-manager \
        ros-humble-foxglove-bridge \
        ros-humble-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# Simulator: f1tenth_gym (Python) + f1tenth_gym_ros (ROS bridge) as an underlay.
# pip quirks copied from upstream gym_ros: a fresh pip is needed for the gym's
# build backend, and on aarch64 + Ubuntu 22.04 PyQt6 must stay at 6.7.1
# (newer wheels need glibc >= 2.39).
RUN if [ "${WITH_SIM}" = "1" ]; then \
        pip3 install --no-cache-dir --ignore-installed pip \
        && echo 'pyqt6 == 6.7.1; platform_machine == "aarch64"' > /tmp/pip-constraints.txt \
        && git clone https://github.com/f1tenth/f1tenth_gym.git /opt/f1tenth_gym \
        && git -C /opt/f1tenth_gym checkout -q ${GYM_REF} \
        && pip3 install --no-cache-dir --ignore-installed -c /tmp/pip-constraints.txt /opt/f1tenth_gym \
        && git clone https://github.com/f1tenth/f1tenth_gym_ros.git /opt/sim_ws/src/f1tenth_gym_ros \
        && git -C /opt/sim_ws/src/f1tenth_gym_ros checkout -q ${GYM_ROS_REF} \
        && apt-get update \
        && rosdep install --from-paths /opt/sim_ws/src --ignore-src --rosdistro humble -y \
        && source /opt/ros/humble/setup.bash \
        && cd /opt/sim_ws && colcon build \
        && rm -rf /opt/sim_ws/build /opt/sim_ws/log /var/lib/apt/lists/*; \
    fi

# Non-root user matching the host's UID/GID, so files in bind mounts stay yours.
# It also owns /opt/sim_ws: gym_bridge_launch.py writes a scaled map copy next to itself.
RUN (getent group ${GID} || groupadd -g ${GID} ${USER}) \
    && useradd -m -s /bin/bash -u ${UID} -g ${GID} -G sudo,dialout,plugdev ${USER} \
    && echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER} \
    && if [ -d /opt/sim_ws ]; then chown -R ${UID}:${GID} /opt/sim_ws; fi

# System deps of everything in ros2_ws/src. Kept last: any change under
# ros2_ws/src re-runs this step, and nothing expensive should sit after it.
COPY ros2_ws/src /tmp/src
RUN apt-get update \
    && (rosdep init 2>/dev/null || true) && rosdep update --rosdistro humble \
    && rosdep install --from-paths /tmp/src --ignore-src --rosdistro humble -y \
        --skip-keys "${ROSDEP_SKIP}" \
    && rm -rf /tmp/src /var/lib/apt/lists/*

# build/install/log are named volumes: a new, empty volume takes the ownership
# of the image directory it is mounted on, so these must exist and be the user's.
RUN mkdir -p /home/${USER}/ws/build /home/${USER}/ws/install /home/${USER}/ws/log \
    && chown -R ${UID}:${GID} /home/${USER}/ws

COPY docker/ros/bashrc_polimi /etc/bashrc_polimi
RUN echo "source /etc/bashrc_polimi" >> /home/${USER}/.bashrc

USER ${USER}
WORKDIR /home/${USER}/ws
CMD ["/bin/bash"]
