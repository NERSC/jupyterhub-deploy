FROM ubuntu:16.04
MAINTAINER Rollin Thomas <rcthomas@lbl.gov>

# Base Ubuntu packages

ENV DEBIAN_FRONTEND noninteractive

RUN \
    apt-get update          &&  \
    apt-get --yes upgrade   &&  \
    apt-get --yes install       \
        bzip2                   \
        curl                    \
        git                     \
        libffi-dev              \
        lsb-release             \
        vim                     \
        wget

# Python 3 Miniconda and dependencies for JupyterHub we can get via conda

RUN \
    wget -q -O /tmp/miniconda3.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh    &&  \
    bash /tmp/miniconda3.sh -f -b -p /opt/anaconda3     &&  \
    rm -rf /tmp/anaconda3.sh                            &&  \
    /opt/anaconda3/bin/conda update --yes conda         &&  \
    /opt/anaconda3/bin/conda install --yes                  \
        decorator       \
        jinja2          \
        mako            \
        markupsafe      \
        nodejs          \
        pyopenssl       \
        python-dateutil \
        sqlalchemy      \
        tornado         \
        traitlets

# Install JupyterHub

WORKDIR /tmp
RUN \
    git clone https://github.com/NERSC/jupyterhub.git   &&  \
    cd jupyterhub                                       &&  \
    git checkout tags/0.8.0-nersc2                      &&  \
    /opt/anaconda3/bin/python setup.py js               &&  \
    /opt/anaconda3/bin/pip install .                    &&  \
    rm -rf ~/.cache ~/.npm

##### # Add gsissh and some other dependencies
##### #  pip install pyopenssl <- from conda
##### 
##### RUN \
#####     echo "deb http://downloads.globus.org/toolkit/gt6/stable/deb/ jessie contrib" >> /etc/apt/sources.list && \
#####     apt-key adv --keyserver  hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44AE7EC2FAF24365 && \
#####     apt-get update && \
#####     apt-get --yes install gsi-openssh-clients
##### 
##### # Add the edisongrid cert
##### ADD ./certs /tmp/certs/
##### RUN \
#####     mkdir /etc/grid-security/certificates/ && \
#####     cp /tmp/certs/* /etc/grid-security/certificates/ && \
#####     pip install git+https://github.com/NERSC/gsiauthenticator.git && \
#####     pip install git+https://github.com/NERSC/sshspawner.git
##### 
##### WORKDIR /srv/
##### EXPOSE 8000
##### 
##### LABEL org.jupyter.service="jupyterhub"
##### 
##### #ADD jupyterhub_config.py /srv/jupyterhub_config.py
##### #CMD ["jupyterhub"]
