# syntax=docker/dockerfile:1
FROM ubuntu:20.04
RUN apt update && apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y ca-certificates sudo apt-utils net-tools
COPY nm-mgmt-collect-http-anon-v0.7.0-arm64-dev1.deb /
RUN dpkg -i nm-mgmt-collect-http-anon-v0.7.0-arm64-dev1.deb
COPY /collectd-http.sh /
RUN chmod u+x /collectd-http.sh
CMD ["/collectd-http.sh"] 
