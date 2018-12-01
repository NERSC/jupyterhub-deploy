ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base.${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"

# Additional Ubuntu packages
# TODO: resolve zsh thing that Rollin ran into b/c datatran

RUN \
    apt-get --yes install   \
        ldap-utils          \
        libnss-ldapd        \
        libpam-ldap         \
        nscd                \
        openssh-server      \
        zsh

# Python 3 Anaconda and additional packages

### TESTING ...

RUN \
    /opt/anaconda3/bin/conda update --yes conda &&  \
    /opt/anaconda3/bin/conda install --yes          \
        ipykernel                                   \
        ipywidgets                                  \
        jupyterlab                                  \
        notebook                                &&  \
    /opt/anaconda3/bin/ipython kernel install   &&  \
    /opt/anaconda3/bin/conda clean --yes --all

# Typical extension

RUN \
    /opt/anaconda3/bin/jupyter nbextension enable --sys-prefix --py widgetsnbextension

### TESTING DONE ...

### ADD packages3.txt /tmp/packages3.txt
### RUN \
###     /opt/anaconda3/bin/conda update --yes conda                 && \
###     /opt/anaconda3/bin/conda install --yes anaconda             && \
###     /opt/anaconda3/bin/conda install --file /tmp/packages3.txt  && \
###     /opt/anaconda3/bin/ipython kernel install                   && \
###     /opt/anaconda3/bin/conda clean --yes --all

### # Python 2 Anaconda and additional packages
### 
### ADD packages2.txt /tmp/packages2.txt
### RUN \
###     wget -q -O /tmp/miniconda2.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  && \
###     bash /tmp/miniconda2.sh -f -b -p /opt/anaconda2             && \
###     rm /tmp/miniconda2.sh                                       && \
###     /opt/anaconda2/bin/conda update --yes conda                 && \
###     /opt/anaconda2/bin/conda install --yes anaconda             && \
###     /opt/anaconda2/bin/conda install --file /tmp/packages2.txt  && \
###     /opt/anaconda2/bin/ipython kernel install                   && \
###     /opt/anaconda2/bin/conda clean --yes --all

# SSHD

RUN \
    mkdir -p /var/run/sshd  && \
    echo "AuthorizedKeysCommand /usr/lib/nersc-ssh-keys/NERSC-keys-api" >> /etc/ssh/sshd_config && \
    echo "AuthorizedKeysCommandUser nobody" >> /etc/ssh/sshd_config && \
    echo "TrustedUserCAKeys /etc/user_ca.pub"  >> /etc/ssh/sshd_config

# PAM, LDAP

COPY etc/ /etc/

# GPFS

RUN \
    mkdir /global                               && \
    ln -sf /global/u1 /global/homes             && \
    ln -sf /global/project /project             && \
    ln -s /global/common/datatran /usr/common   && \
    echo "datatran" > /etc/clustername

ADD docker-entrypoint.sh /srv/
ADD NERSC-keys-api /usr/lib/nersc-ssh-keys/
ADD get_port.py /opt/anaconda3/bin/
RUN chmod a+x /usr/lib/nersc-ssh-keys/NERSC-keys-api

WORKDIR /srv
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "/usr/sbin/sshd", "-p", "22", "-D" ]
