FROM registry.spin.nersc.gov/das/jupyterhub-base:latest
MAINTAINER Rollin Thomas <rcthomas@lbl.com>

# JupyterHub components

RUN \
    pip install git+https://github.com/NERSC/sshspawner.git

# Some dummy users

RUN \
    adduser -q --gecos "" --disabled-password torgo     && \
    echo torgo:the-master-would-not-approve | chpasswd

RUN \
    adduser -q --gecos "" --disabled-password master    && \
    echo master:you-have-failed-us-torgo | chpasswd

WORKDIR /srv
ADD docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
CMD ["jupyterhub", "--debug"]
ENTRYPOINT ["./docker-entrypoint.sh"]
