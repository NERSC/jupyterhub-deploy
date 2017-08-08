FROM nersc/jupyterhub:latest
MAINTAINER Shane Canon <scanon@lbl.gov>

# Add gsissh and some other dependencies
RUN \
  apt-get -y update && \
  apt-get -y install libffi-dev curl lsb-release && \
  pip install pyopenssl && \
  wget http://www.lsc-group.phys.uwm.edu/lscdatagrid/doc/ldg-client.sh -O /tmp/ldg-client.sh && \
  bash /tmp/ldg-client.sh

# Add the edisongrid cert
ADD ./certs /tmp/certs/
RUN cp /tmp/certs/* /etc/grid-security/certificates/ && \
    pip install git+https://github.com/NERSC/gsiauthenticator.git && \
    pip install git+https://github.com/NERSC/sshspawner.git

WORKDIR /srv/
EXPOSE 8000

LABEL org.jupyter.service="jupyterhub"

ADD jupyterhub_config.py /srv/jupyterhub_config.py
CMD ["jupyterhub"]
