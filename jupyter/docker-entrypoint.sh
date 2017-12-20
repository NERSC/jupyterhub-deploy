#!/bin/bash

service rsyslog restart
service nslcd restart

ip addr

exec "$@"
