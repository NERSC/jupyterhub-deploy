#!/bin/bash

for u in $(ls /home/) ; do
  cp /config/newkey /tmp/$u.key
  chmod 600 /tmp/$u.key
done

exec "$@"
