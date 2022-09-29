# syntax=docker/dockerfile:1
FROM ubuntu:20.04
RUN apt update && apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y ca-certificates sudo apt-utils cron net-tools traceroute iputils-ping dnsutils nmap logrotate python3 python3-pip
RUN yes | DEBIAN_FRONTEND=teletype apt install  -y tshark
COPY nm-exp-active-netrics-v1.0.0-arm64.deb /
RUN dpkg -i nm-exp-active-netrics-v1.0.0-arm64.deb
COPY volume/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml /etc/nm-exp-active-netrics/
CMD ["cron", "-f"]
