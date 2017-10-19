FROM postgres:10.0
MAINTAINER Rollin Thomas <rcthomas@lbl.com>

RUN \
    mkdir -p /docker-entrypoint-initdb.d

COPY initdb.sh /docker-entrypoint-initdb.d/init.sh
