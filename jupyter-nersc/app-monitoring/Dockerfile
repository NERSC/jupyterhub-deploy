FROM ubuntu:focal
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"
WORKDIR /srv

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN \
    apt-get update          &&  \
    apt-get upgrade --yes   &&  \
    apt-get install             \
        --no-install-recommends \
        --yes                   \
        python3-pip             \
        tzdata

ENV TZ=America/Los_Angeles
RUN \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime  &&  \
    echo $TZ > /etc/timezone

RUN \
    pip3 install --no-cache-dir \
        pika                    \
        requests

ADD monitor.py .
ADD docker-entrypoint.sh .

RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "monitor.py"]
