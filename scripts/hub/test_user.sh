#!/bin/sh

USER=$1
shift
X509_USER_CERT=/tmp/x509_${USER} X509_USER_KEY=/tmp/x509_${USER}  gsissh -v -o StrictHostKeyChecking=no -l ${USER} -p 2222 cori19-224.nersc.gov $@
