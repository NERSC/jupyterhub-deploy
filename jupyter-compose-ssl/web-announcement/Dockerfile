ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

RUN \
    pip install git+https://github.com/rcthomas/jupyterhub-announcement.git@0.4.1

WORKDIR /srv

ADD docker-entrypoint.sh announcement_config.py ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "jupyterhub_announcement"]
