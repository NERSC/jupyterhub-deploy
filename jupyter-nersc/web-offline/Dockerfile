FROM ubuntu:18.04
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

# Base Ubuntu packages

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN \
    apt-get update          &&  \
    apt-get --yes upgrade   &&  \
    apt-get --yes install       \
        bzip2                   \
        curl                    \
        git                     \
        tzdata                  \
        vim

# Timezone to Berkeley

ENV TZ=America/Los_Angeles
RUN \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime  &&  \
    echo $TZ > /etc/timezone

# Miniconda

RUN \
    curl -s -o /tmp/miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&  \
    bash /tmp/miniconda3.sh -b -p /opt/anaconda3            &&  \
    rm -rf /tmp/miniconda3.sh                               &&  \
    echo "python 3.7.3" >> /opt/anaconda3/conda-meta/pinned &&  \
    /opt/anaconda3/bin/conda update --yes conda             &&  \
    /opt/anaconda3/bin/conda clean --yes --all

ENV PATH=/opt/anaconda3/bin:$PATH

# Packages

# RUN \
#     conda install --yes         \
#         --channel=conda-forge   \
#         jinja2                  \
#         sanic

# Temporary off master, sanic bug: https://github.com/huge-success/sanic/issues/1773

RUN \
    conda install --yes             \
        --channel=conda-forge       \
        aiofiles                    \
        brotlipy                    \
        h11=0.8.1                   \
        h2                          \
        hpack                       \
        hstspreload                 \
        httptools                   \
        httpx=0.9.3                 \
        hyperframe                  \
        jinja2                      \
        markupsafe                  \
        multidict                   \
        rfc3986                     \
        sniffio                     \
        ujson                       \
        uvloop                      \
        websockets              &&  \
    pip install --no-cache-dir git+https://github.com/huge-success/sanic        

# Application

WORKDIR /srv
ADD app.py /srv/
ADD templates /srv/templates
ADD static /srv/static

CMD ["python", "-m", "sanic", "app.app", "--host=0.0.0.0", "--workers=4"]
