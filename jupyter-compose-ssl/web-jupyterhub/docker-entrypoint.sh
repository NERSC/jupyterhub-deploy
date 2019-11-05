#!/bin/bash

for u in $(ls /home/) ; do
  cp /config/newkey /tmp/$u.key
  chmod 600 /tmp/$u.key
  cp /config/newkey-cert.pub /tmp/$u.key-cert.pub
  chmod 600 /tmp/$u.key-cert.pub
done

exec "$@"
