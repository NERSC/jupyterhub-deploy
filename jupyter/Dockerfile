FROM nersc/jupyterhub-base:latest
MAINTAINER Rollin Thomas <rcthomas@lbl.com>

# Additional Ubuntu packages

RUN \
    apt-get --yes install   \
        ldap-utils          \
        libnss-ldapd        \
        libpam-ldap         \
        nscd

# LDAP

ADD ldap /tmp/ldap
RUN \
    mkdir -p  /etc/httpd/ssl && \
    cp /tmp/ldap/ldap.conf /etc/ldap/ldap.conf && \
    cp /tmp/ldap/nslcd.conf /etc/nslcd.conf && \
    cp /tmp/ldap/nsswitch.conf /etc/nsswitch.conf && \
    cp /tmp/ldap/pam_ldap.conf /etc/pam_ldap.conf && \
    cp /tmp/ldap/password-auth /etc/pam.d/password-auth && \
    mkdir /global && \
    ln -sf /global/u1 /global/homes && \
    ln -sf /global/project /project && \
    ln -s /global/common/datatran /usr/common && \
    echo "datatran" > /etc/clustername

# Python 3 Anaconda and additional packages

ADD packages3.txt /tmp/packages3.txt
RUN \
    /opt/anaconda3/bin/conda update --yes conda                 && \
    /opt/anaconda3/bin/conda install --yes anaconda             && \
    /opt/anaconda3/bin/conda install --file /tmp/packages3.txt  && \
    /opt/anaconda3/bin/ipython kernelspec install-self          && \
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
    /opt/anaconda2/bin/ipython kernelspec install-self          && \
    /opt/anaconda2/bin/conda clean --yes --all

ADD jupyterhub /srv/
RUN mv /srv/jupyterhub.pamd /etc/pam.d/jupyterhub

ADD entrypoint.sh /entrypoint.sh
 
EXPOSE 80 443
WORKDIR /srv
ENTRYPOINT [ "/entrypoint.sh" ]
CMD  []
