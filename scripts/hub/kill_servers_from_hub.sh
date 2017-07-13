#!/bin/bash

# Calls kill_old_servers.py on cori to kill notebook
# processes owned by a user except the latest one


credlist=`ls /tmp/x509*`
for cred in $credlist; do
    user=`echo $cred | awk -F "x509_" '{print $2}'` 
    export X509_USER_CERT=$cred
    export X509_USER_KEY=$cred
    output=$(gsissh -o StrictHostKeyChecking=no -l $user -p 2222  cori19-224.nersc.gov /global/common/cori/software/python/2.7-anaconda/bin/python /global/common/cori/das/jupyterhub/kill_old_servers.py --username $user)
    echo $output
done
    
