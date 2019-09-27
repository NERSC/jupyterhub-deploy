ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

# JupyterHub components

RUN \
    pip install git+https://github.com/NERSC/sshspawner.git@clean-up

# Some dummy users

RUN \
    adduser -q --gecos "" --disabled-password torgo     && \
    echo torgo:the-master-would-not-approve | chpasswd

RUN \
    adduser -q --gecos "" --disabled-password master    && \
    echo master:you-have-failed-us-torgo | chpasswd

WORKDIR /srv
ADD docker-entrypoint.sh .
ADD jupyterhub_config.py .
ADD templates templates
RUN chmod +x docker-entrypoint.sh
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

CMD ["jupyterhub", "--debug"]
ENTRYPOINT ["./docker-entrypoint.sh"]
