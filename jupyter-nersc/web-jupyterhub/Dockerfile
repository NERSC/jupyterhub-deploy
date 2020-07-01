ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"
WORKDIR /srv

# Authenticator and spawner

RUN \
    pip install git+https://github.com/nersc/sshapiauthenticator.git            &&  \
    pip install git+https://github.com/jupyterhub/batchspawner.git@v1.0.0-rc0   &&  \
    pip install git+https://github.com/jupyterhub/wrapspawner.git               &&  \
    pip install git+https://github.com/nersc/sshspawner.git

# Customized templates

ADD templates templates

# FIXME Install this stuff

ENV PYTHONPATH=/srv
ADD nerscspawner.py .
ADD nerscslurmspawner.py .
ADD iris.py .
ADD spinproxy.py .

# Hub scripts

ADD hub-scripts/*.sh /srv/

# Volume for user cert/key files

VOLUME /certs

# Entrypoint and command

ADD docker-entrypoint.sh jupyterhub_config.py /srv/
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["jupyterhub", "--debug"]
