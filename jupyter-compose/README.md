# Developing with docker-compose

These images are designed for local dev/debug/testing using docker-compose.
This requires docker-compose.

## Preparation

Install Docker Compose (Just google for it).

Build the images

    cd web-jupyterhub && bash build.sh && cd ..
    cd app-notebooks && bash build.sh && cd ..

Generate a key file

    mkdir config
    ssh-keygen -t rsa -N '' -C ca@localhost -f config/newkey
    ssh-keygen -s config/newkey -h -I localhost config/newkey.pub

## Bring up the containers

    docker-compose up -d

## Cleaning up and upgrading

In general a docker-compose up -d will refresh things.  Some times that isn't enough.  If all else fails, try...

    docker-compose stop
    docker-compose rm -f
