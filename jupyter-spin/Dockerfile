FROM registry.spin.nersc.gov/das/jupyterhub-base.gaffer:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

# Additional Ubuntu packages

RUN \
    apt-get update      &&      \
    apt-get install --yes       \
        --no-install-recommends \
        csh                     \
        dvipng                  \
        ldap-utils              \
        libnss-ldapd            \
        libpam-ldap             \
        nscd                    \
        rsyslog                 \
        supervisor              \
        texlive-xetex           \
        zsh

# Python 3 Anaconda and additional packages

ADD packages3.txt /tmp/packages3.txt
RUN \
    /opt/anaconda3/bin/conda update --yes conda                 && \
    /opt/anaconda3/bin/conda install --yes anaconda             && \
    /opt/anaconda3/bin/conda install --file /tmp/packages3.txt  && \
    /opt/anaconda3/bin/ipython kernel install                   && \
    /opt/anaconda3/bin/conda clean --yes --all

# Python 2 Anaconda and additional packages

ADD packages2.txt /tmp/packages2.txt
RUN \
    curl -s -o /tmp/miniconda2.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  && \
    bash /tmp/miniconda2.sh -f -b -p /opt/anaconda2             && \
    rm /tmp/miniconda2.sh                                       && \
    /opt/anaconda2/bin/conda update --yes conda                 && \
    /opt/anaconda2/bin/conda install --yes anaconda             && \
    /opt/anaconda2/bin/conda install --file /tmp/packages2.txt  && \
    /opt/anaconda2/bin/ipython kernel install                   && \
    /opt/anaconda2/bin/conda clean --yes --all

# PAM, LDAP

COPY etc/ /etc/

# GPFS

RUN \
    mkdir /global                               && \
    ln -sf /global/u1 /global/homes             && \
    ln -sf /global/project /project             && \
    ln -s /global/common/datatran /usr/common   && \
    echo "datatran" > /etc/clustername

# Jupyterhub features

RUN \
    /opt/anaconda3/bin/jupyter nbextension enable --sys-prefix --py widgetsnbextension      && \
    /opt/anaconda2/bin/jupyter nbextension enable --sys-prefix --py widgetsnbextension      && \
    /opt/anaconda3/bin/jupyter labextension install @jupyterlab/hub-extension

# Config and entrypoint script

ADD docker-entrypoint.sh jupyterhub_config.py /srv/
 
WORKDIR /srv

# TEMPORARILY HERE: Set up supervisord

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
