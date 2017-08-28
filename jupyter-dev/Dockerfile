FROM nersc/jupyterhub-base:latest
MAINTAINER Rollin Thomas <rcthomas@lbl.com>

# Add gsissh

RUN \
  echo "deb http://downloads.globus.org/toolkit/gt6/stable/deb/ jessie contrib" >> /etc/apt/sources.list && \
  apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44AE7EC2FAF24365 && \
  apt-get update && \
  apt-get --yes install gsi-openssh-clients

# Add edisongrid cert

ADD ./certs /tmp/certs/
RUN \
    mkdir /etc/grid-security/certificates/ && \
    cp /tmp/certs/* /etc/grid-security/certificates/ && \
    pip install git+https://github.com/NERSC/gsiauthenticator.git && \
    pip install git+https://github.com/NERSC/sshspawner.git@v0.8updates

WORKDIR /srv/
EXPOSE 8000

LABEL org.jupyter.service="jupyterhub"

ADD jupyterhub_config.py /srv/jupyterhub_config.py
CMD ["jupyterhub"]
