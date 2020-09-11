#!/bin/bash

# Useful when JupyterHub thinks a user has no server running
# but actually they do, and they still have a cert.

hostname=$1
username=$2
cert=/certs/$username.key
echo $username $cert
if [ ! -f $cert ]; then
    echo " ... SKIPPED no cert for $username"
    continue
fi

if [ "$#" -lt 3 ]; then
    for i in 1 2 3
    do
        /usr/bin/ssh                                \
            -i $cert                                \
            -l $username                            \
            -o PreferredAuthentications=publickey   \
            -o StrictHostKeyChecking=no             \
            -p 22                                   \
            $hostname                               \
            killall -u $username
        sleep 1
    done
elif [ "$#" -ge 3 ]; then
    /usr/bin/ssh                                \
        -i $cert                                \
        -l $username                            \
        -o PreferredAuthentications=publickey   \
        -o StrictHostKeyChecking=no             \
        -p 22                                   \
        $hostname                               \
        kill -9 "${@:3}"
fi
