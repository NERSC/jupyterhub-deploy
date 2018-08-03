#!/bin/bash

# Test a user's ability to gsissh in.

username=$1
cert=/certs/x509_$username
echo $username $cert
if [ ! -f $cert ]; then
    echo " ... no cert for $username"
    exit 1
fi
export X509_USER_CERT=$cert
export X509_USER_KEY=$cert
gsissh \
    -o StrictHostKeyChecking=no \
    -l $username \
    -p 2222 cori19-224.nersc.gov
