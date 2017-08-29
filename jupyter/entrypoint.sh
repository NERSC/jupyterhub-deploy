#!/bin/bash -l

service rsyslog restart
service nslcd restart

ip addr
export PATH=$PATH:/opt/anaconda3/bin/

if [ ! "$STARTSHELL" == "" ]
then  
  /bin/bash
else 
  node /srv/redirect.js https://ipython.nersc.gov &
  /opt/anaconda3/bin/jupyterhub --debug
fi
