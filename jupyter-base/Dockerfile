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
        libffi-dev              \
        lsb-release             \
        tzdata                  \
        vim                     \
        wget

# Timezone to Berkeley

ENV TZ=America/Los_Angeles
RUN \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime  &&  \
    echo $TZ > /etc/timezone

# Python 3 Miniconda and dependencies for JupyterHub we can get via conda

RUN \
    curl -s -o /tmp/miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&  \
    bash /tmp/miniconda3.sh -b -p /opt/anaconda3            &&  \
    rm -rf /tmp/miniconda3.sh                               &&  \
    /opt/anaconda3/bin/conda update --yes conda             &&  \
    /opt/anaconda3/bin/conda install --yes                      \
	--channel conda-forge \
        alembic             \
        attrs               \
        certipy             \
        cryptography        \
        decorator           \
        entrypoints         \
        jinja2              \
        jsonschema          \
        mako                \
        markupsafe          \
        more-itertools      \
        nodejs              \
        oauthlib            \
        pamela              \
        psycopg2            \
        pycurl              \
        pyopenssl           \
        pyrsistent          \
        python-dateutil     \
        python-editor       \
        ruamel.yaml         \
        ruamel.yaml.clib    \
        sqlalchemy          \
        tornado             \
        traitlets=4.3.3     \
        zipp

# Install JupyterHub

ENV PATH=/opt/anaconda3/bin:$PATH
WORKDIR /tmp
RUN \
    npm install -g configurable-http-proxy                                  &&  \
    git clone https://github.com/jupyterhub/jupyterhub.git                  &&  \
    cd jupyterhub                                                           &&  \
#   git checkout tags/1.1.0                                                 &&  \
    /opt/anaconda3/bin/python setup.py js                                   &&  \
    /opt/anaconda3/bin/pip --no-cache-dir install .                         &&  \
    rm -rf ~/.cache ~/.npm
