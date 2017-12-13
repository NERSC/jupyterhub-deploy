FROM registry.spin.nersc.gov/das/jupyterhub-base:latest
MAINTAINER Rollin Thomas <rcthomas@lbl.com>

# Additional Ubuntu packages

RUN \
    apt-get --yes install   \
        ldap-utils          \
        libnss-ldapd        \
        libpam-ldap         \
        nscd                \
        texlive-xetex

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
    wget -q -O /tmp/miniconda2.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  && \
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

# Config and entrypoint script

ADD docker-entrypoint.sh jupyterhub /srv/
 
WORKDIR /srv
RUN chmod +x docker-entrypoint.sh
CMD ["jupyterhub", "--debug"]
ENTRYPOINT ["./docker-entrypoint.sh"]
