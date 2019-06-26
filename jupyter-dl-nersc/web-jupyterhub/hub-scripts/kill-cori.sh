#!/bin/bash

# Shut down all but the newest jupyterhub server running.

hostname=$1
username=$2
cert=/certs/$username.key
echo $username $cert
if [ ! -f $cert ]; then
    echo " ... no cert for $username"
    exit 1
fi
/usr/bin/ssh                                \
    -i $cert                                \
    -l $username                            \
    -o PreferredAuthentications=publickey   \
    -o StrictHostKeyChecking=no             \
    -p 22                                   \
    $hostname                               \
    /global/common/shared/das/jupyterhub/kill-my-old-jupyters.sh
