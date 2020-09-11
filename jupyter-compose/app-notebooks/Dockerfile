ARG branch=unknown

FROM registry.spin.nersc.gov/das/jupyter-base-${branch}:latest
LABEL maintainer="Rollin Thomas <rcthomas@lbl.gov>"
WORKDIR /tmp

RUN \
    apt-get update          &&  \
    apt-get --yes upgrade   &&  \
    apt-get --yes install       \
        openssh-server

# Configure sshd

RUN \
    mkdir -p /var/run/sshd

# Python 3 Anaconda and additional packages

RUN \
    conda update --yes conda    &&  \
    conda install --yes             \
        ipykernel                   \
        ipywidgets                  \   
        jupyterlab                  \
        notebook                &&  \
    ipython kernel install      &&  \
    conda clean --yes --all

ADD get_port.py /opt/anaconda3/bin

# Typical extensions

RUN \
    jupyter nbextension enable --sys-prefix --py widgetsnbextension

RUN \
    jupyter labextension install @jupyterlab/hub-extension

# Jupyter server proxy

RUN \
    pip install --no-cache-dir \
        git+https://github.com/jupyterhub/jupyter-server-proxy.git

ADD jupyter_notebook_config.py /opt/anaconda3/etc/jupyter/.

#### # Jupyter server proxy; install but don't enable
#### 
#### RUN \
####     pip install --no-cache-dir \
####         jupyter-server-proxy
#### 
#### ADD jupyter-server-mapper /tmp/jupyter-server-mapper
#### RUN \
####     cd /tmp/jupyter-server-mapper   &&  \
####     python setup.py install         &&  \
####     cd -                            &&  \
####     jupyter serverextension enable --py jupyter_server_mapper --sys-prefix
#### 
#### ADD jupyter_notebook_config.py /opt/anaconda3/etc/jupyter/.

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
