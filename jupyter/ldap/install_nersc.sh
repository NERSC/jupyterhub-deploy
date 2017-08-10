#!/bin/bash -l

source `dirname $0`/setup.sh

yum install -y wget
yum install -y nss-pam-ldapd openldap 


mkdir -p  /etc/httpd/ssl

cp $CONTEXTPATH/ldap.conf /etc/openldap/ldap.conf
cp $CONTEXTPATH/nslcd.conf /etc/nslcd.conf
cp $CONTEXTPATH/nsswitch.conf /etc/nsswitch.conf
cp $CONTEXTPATH/pam_ldap.conf /etc/pam_ldap.conf
cp $CONTEXTPATH/password-auth /etc/pam.d/password-auth
cp $CONTEXTPATH/sshd.pamd /etc/pam.d/sshd
cp $CONTEXTPATH/startall.sh /etc/startall.sh

service nslcd restart


mkdir /global
ln -sf /global/u1 /global/homes
ln -sf /global/project /project
ln -s /global/common/datatran /usr/common
echo "datatran" > /etc/clustername
