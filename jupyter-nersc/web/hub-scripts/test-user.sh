#!/bin/bash

# Test user's ability to ssh

hostname=app
username=$1
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
    $hostname
