ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyterhub-base.${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"
WORKDIR /srv

# Authenticator and spawner

RUN \
    pip install git+https://github.com/nersc/sshapiauthenticator.git    && \
    pip install git+https://github.com/nersc/sshspawner.git

# MFA-enabled login template

ADD templates templates

# Install announcement service components

RUN \
    cp /tmp/jupyterhub/examples/service-announcement/announcement.py .  &&  \
    cp /tmp/jupyterhub/examples/service-announcement/templates/page.html templates/.

# Hub scripts

ADD hub-scripts/*.sh /srv/

# Volume for user cert/key files

VOLUME /certs

# Entrypoint and command

ADD docker-entrypoint.sh jupyterhub_config.py /srv/
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["jupyterhub", "--debug"]
