ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

RUN \
    pip install --no-cache-dir jupyterhub-idle-culler

WORKDIR /srv

ADD docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "-m", "jupyterhub_idle_culler", "--timeout=57600", "--cull-every=3600", "--url=http://web-jupyterhub:8081/hub/api"]
