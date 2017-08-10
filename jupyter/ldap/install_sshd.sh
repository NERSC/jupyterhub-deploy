#!/bin/bash -l

source `dirname $0`/setup.sh

yum install -y openssh-server openssh-clients syslog
echo "UsePrivilegeSeparation no" >> /etc/ssh/sshd_config

service rsyslog restart
service sshd restart

