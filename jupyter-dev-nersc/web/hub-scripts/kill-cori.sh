#!/bin/bash

# If usernames provided, shut down all but the newest jupyterhub server running.
# Else get usernames from /certs, then shut down all but newest server running.

usernames=("$@")
if [ ${#usernames[@]} -eq 0 ]; then
    for cert in /certs/*.key
    do
        username=$(echo $cert | cut -b8- | sed 's/\.key$//')
        usernames=(${usernames[@]} $username)
    done
fi

for username in ${usernames[@]}
do
    cert=/certs/$username.key
    echo $username $cert
    if [ ! -f $cert ]; then
        echo " ... SKIPPED no cert for $username"
        continue
    fi
    /usr/bin/ssh                                \
        -i $cert                                \
        -l $username                            \
        -o PreferredAuthentications=publickey   \
        -o StrictHostKeyChecking=no             \
        -p 22                                   \
        cori19-224.nersc.gov                    \
        /global/common/shared/das/jupyterhub/kill-my-old-jupyters.sh
    sleep 1
done
