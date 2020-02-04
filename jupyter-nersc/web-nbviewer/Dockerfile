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
    conda install --yes --all   \
        invoke                  \
        markdown                \
        nbconvert               \
        nbformat                \
        notebook                \
        pycurl              &&  \
    pip install --no-cache-dir  \
        statsd

WORKDIR /repos

RUN \
    git clone --single-branch --branch develop https://github.com/krinsman/nbviewer.git   &&  \
    cd nbviewer  &&  \
# --no-dependencies flag because we don't actually need pylibmc or elasticsearch to run this (without
# elasticsearch or memcached) and everything else in requirements.txt is already installed
    pip install -e . --no-cache-dir --no-dependencies   &&  \
    npm install     &&  \
    invoke bower    &&  \
    invoke less     &&  \
    cd ..

RUN \
    git clone https://github.com/krinsman/clonenotebooks.git    &&  \
    cd clonenotebooks               &&  \
#    git checkout NERSC              &&  \
    pip install -e . --no-cache-dir &&  \
    cd ..

WORKDIR /srv

ADD docker-entrypoint.sh nbviewer_config.py ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "nbviewer"]
