#!/bin/bash

# Kill them all!
# Useful when JupyterHub thinks a user has no server running
# but actually they do, and they still have a cert.

for username in "$@"
do
    cert=/certs/x509_$username
    echo $username $cert
    if [ ! -f $cert ]; then
        echo " ... SKIPPED no cert for $username"
        continue
    fi
    export X509_USER_CERT=$cert
    export X509_USER_KEY=$cert
    for i in 1 2 3
    do
        gsissh \
            -o StrictHostKeyChecking=no \
            -l $username \
            -p 2222 cori19-224.nersc.gov \
            killall -u $username
        sleep 1
    done
done
