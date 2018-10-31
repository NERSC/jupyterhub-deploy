#!/bin/bash

# Kill them all!
# Useful when JupyterHub thinks a user has no server running
# but actually they do, and they still have a cert.

for username in "$@"
do
    cert=/certs/$username.key
    echo $username $cert
    if [ ! -f $cert ]; then
        echo " ... SKIPPED no cert for $username"
        continue
    fi
    for i in 1 2 3
    do
        /usr/bin/ssh                                \
            -i $cert                                \
            -l $username                            \
            -o PreferredAuthentications=publickey   \
            -o StrictHostKeyChecking=no             \
            -p 22                                   \
            cori19-224.nersc.gov                    \
            killall -u $username
        sleep 1
    done
done
