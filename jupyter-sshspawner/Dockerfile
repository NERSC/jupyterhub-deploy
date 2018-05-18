FROM ubuntu:16.04
MAINTAINER Rollin Thomas <rcthomas@lbl.gov>
WORKDIR /tmp

# Base Ubuntu packages

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN \
    apt-get update          &&  \
    apt-get --yes upgrade   &&  \
    apt-get --yes install       \
        bzip2                   \
        curl                    \
        openssh-server          \
        vim

# Configure sshd

RUN \
    mkdir -p /var/run/sshd

### ADD NERSC-keys-api /usr/lib/nersc-ssh-keys/
### RUN chmod a+x /usr/lib/nersc-ssh-keys/NERSC-keys-api
##
### RUN \
###     echo "AuthorizedKeysCommand /usr/lib/nersc-ssh-keys/NERSC-keys-api" >> /etc/ssh/sshd_config && \
###     echo "AuthorizedKeysCommandUser nobody" >> /etc/ssh/sshd_config

# Python 3 Anaconda and additional packages

RUN \
    curl --output miniconda3.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh   &&  \
    bash miniconda3.sh -f -b -p /opt/anaconda3  &&  \
    rm -rf miniconda3.sh

ENV PATH /opt/anaconda3/bin:$PATH

RUN \
    conda update --yes conda    &&  \
    conda install --yes             \
        ipykernel                   \
        ipywidgets                  \
        notebook                &&  \
    ipython kernel install      &&  \
    conda clean --yes --all

ADD get_port.py /opt/anaconda3/bin

# Typical extension

RUN \
    jupyter nbextension enable --sys-prefix --py widgetsnbextension

# Some dummy users

RUN \
    adduser -q --gecos "" --disabled-password torgo     && \
    echo torgo:the-master-would-not-approve | chpasswd

RUN \
    adduser -q --gecos "" --disabled-password master    && \
    echo master:you-have-failed-us-torgo | chpasswd

WORKDIR /srv
ADD docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "/usr/sbin/sshd", "-p", "22", "-D" ]
