# syntax=docker/dockerfile:1
#FROM balenalib/%%BALENA_MACHINE_NAME%%-ubuntu:focal
FROM ubuntu:focal
RUN apt update && apt upgrade -y && DEBIAN_FRONTEND=noninteractive apt install -y ca-certificates \
    sudo apt-utils cron net-tools traceroute iputils-ping dnsutils nmap logrotate python3 python3-pip \
    iproute2 snapd python3-opencv xvfb python3-tk scrot xclip xdg-utils xdg-utils chromium-browser httping libjemalloc2
RUN addgroup --gid 1001 netrics && \
    adduser --uid 1001 --gid 1001 \
      --disabled-password --gecos "" \
      netrics

COPY nm-exp-active-netrics-v1.0.0-arm64.deb /
RUN dpkg -i nm-exp-active-netrics-v1.0.0-arm64.deb
COPY cron-install-netrics-cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/cron-install-netrics-cron
RUN touch /var/log/cron.log
COPY install-netrics-cron.sh /
RUN chmod a+x install-netrics-cron.sh
COPY cron.sh /
RUN chmod a+x /cron.sh
CMD ["/cron.sh"]
