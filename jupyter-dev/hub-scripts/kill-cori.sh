#!/bin/bash

# If usernames provided, shut down all but the newest jupyterhub server running.
# Else get usernames from /certs, then shut down all but newest server running.

usernames=("$@")
if [ ${#usernames[@]} -eq 0 ]; then
    for cert in /certs/x509_*
    do
        username=$(echo $cert | cut -b 13-)
        usernames=(${usernames[@]} $username)
    done
fi

for username in ${usernames[@]}
do
    cert=/certs/x509_$username
    echo $username $cert
    if [ ! -f $cert ]; then
        echo " ... SKIPPED no cert for $username"
        continue
    fi
    export X509_USER_CERT=$cert
    export X509_USER_KEY=$cert
    gsissh \
        -o StrictHostKeyChecking=no \
        -l $username \
        -p 2222 cori19-224.nersc.gov \
        /global/common/shared/das/jupyterhub/kill-my-old-jupyters.sh
    sleep 1
done
