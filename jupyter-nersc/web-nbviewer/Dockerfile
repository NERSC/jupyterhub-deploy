ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

#RUN \
#    apt-get --yes install   &&  \
#    libcurl4-openssl-dev        \
#    libgnutls28-dev             \
#    libzmq3-dev                 \
#    libevent-dev

RUN \
    conda install -c conda-forge --yes --all   \
        invoke                  \
        markdown                \
        nbconvert               \
        nbformat                \
        notebook                \
        pylibmc                 \
        pycurl              &&  \
    pip install --no-cache-dir  \
        statsd

WORKDIR /repos

RUN \
    git clone https://github.com/jupyter/nbviewer.git   &&  \
    cd nbviewer  &&  \
    # --no-dependencies flag because we don't actually need pylibmc or elasticsearch to run this (without
    # elasticsearch or memcached) and everything else in requirements.txt is already installed
    pip install -e . --no-cache-dir --no-dependencies   &&  \
    npm install     &&  \
    invoke bower    &&  \
    invoke less     &&  \
    cd ..

RUN echo "Building clonenotebooks"
RUN \
    git clone https://github.com/NERSC/clonenotebooks.git   &&  \
    cd clonenotebooks               &&  \
    pip install -e . --no-cache-dir &&  \
    cd ..

WORKDIR /srv

ADD frontpage.json ./

ADD docker-entrypoint.sh nbviewer_config.py ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "nbviewer", "--no-cache"]
