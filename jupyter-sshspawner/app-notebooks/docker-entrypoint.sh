#!/bin/bash

for u in $(ls /home/) ; do 
  mkdir /home/$u/.ssh/
  cat /config/newkey.pub > /home/$u/.ssh/authorized_keys
  chmod 700 /home/$u/.ssh/
  chown -R $u /home/$u/.ssh
  chmod 600 /home/$u/.ssh/authorized_keys
done

exec "$@"
