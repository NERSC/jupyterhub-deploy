FROM registry.spin.nersc.gov/das/jupyterhub-base.deploy-august-14:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

# Install gsissh

RUN \
    apt-get update              &&  \
    apt-get install --yes           \
        apt-transport-https     &&  \
    echo "deb http://downloads.globus.org/toolkit/gt6/stable/deb/ jessie contrib" >> /etc/apt/sources.list && \
    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44AE7EC2FAF24365 && \
    apt-get update              &&  \
    apt-get install --yes           \
        gsi-openssh-clients

# Add certs

ADD certs /etc/grid-security/certificates

# JupyterHub GSI Authenticator and SSH Spawner from NERSC
  
RUN \
    pip install --no-cache-dir git+https://github.com/NERSC/gsiauthenticator.git && \
    pip install --no-cache-dir git+https://github.com/NERSC/sshspawner.git

# Volume for user cert/key files

VOLUME /certs

# Config and entrypoint script

ADD jupyterhub_config.py docker-entrypoint.sh /srv/
ADD hub-scripts/*.sh /srv/

WORKDIR /srv
RUN chmod +x docker-entrypoint.sh
CMD ["jupyterhub", "--debug"]
ENTRYPOINT ["./docker-entrypoint.sh"]
