FROM ubuntu:focal as base

COPY ./test/config.yaml /etc/prom2flock/config.yaml
COPY ./src /opt
COPY ./requirements.txt /opt

RUN apt update && apt install -y python3 python3-pip && \
    /usr/bin/pip3 install -r /opt/requirements.txt &&\
    apt remove -y python3-pip && apt autoremove -y && \
    mkdir -p /var/log/prom2flock && \
    mkdir -p /var/log/prom2flock/log && \
    mkdir -p /var/log/prom2flock/error && \
    mkdir -p /var/run/prom2flock && \
    adduser prom2flock --system --no-create-home && \
    groupadd -f prom2flock

EXPOSE 5009
WORKDIR /opt/
ENTRYPOINT [ "./prom2flock" ]