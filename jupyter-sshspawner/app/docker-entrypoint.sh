#!/bin/bash

for u in $(ls /home/) ; do 
  mkdir /home/$u/.ssh/
  cat /config/newkey.pub > /home/$u/.ssh/authorized_keys
  chmod 700 /home/$su/.ssh/
  chown -R $u /home/$u/.ssh
  chmod 600 /home/$su/.ssh/authorized_keys
done

exec "$@"
