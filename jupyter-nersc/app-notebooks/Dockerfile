FROM ubuntu:16.04
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
        wget                    \
        csh                     \
        ksh                     \
        ldap-utils              \
        libnss-ldapd            \
        libpam-ldap             \
        libxrender-dev          \
        nscd                    \
        openssh-server          \
        supervisor              \
        tcsh                    \
        zsh

# Timezone to Berkeley

ENV TZ=America/Los_Angeles
RUN \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime  &&  \
    echo $TZ > /etc/timezone

# For ssh auth API

ADD NERSC-keys-api /usr/lib/nersc-ssh-keys/
RUN chmod a+x /usr/lib/nersc-ssh-keys/NERSC-keys-api

# For sshd

RUN \
    mkdir -p /var/run/sshd  && \
    echo "AuthorizedKeysCommand /usr/lib/nersc-ssh-keys/NERSC-keys-api" >> /etc/ssh/sshd_config && \
    echo "AuthorizedKeysCommandUser nobody" >> /etc/ssh/sshd_config && \
    echo "TrustedUserCAKeys /etc/user_ca.pub"  >> /etc/ssh/sshd_config

# For PAM/LDAP

COPY etc/ /etc/

# NGF

RUN \
    mkdir /global                               && \
    ln -sf /global/u1 /global/homes             && \
    ln -sf /global/project /project             && \
    ln -s /global/common/cori_cle7 /usr/common  && \
    echo "datatran" > /etc/clustername

# Supervisord to launch sshd and nslcd

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
