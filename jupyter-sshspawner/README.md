# SSHSpawner Testing

These images are designed for local testing of the SSH Spawner.  This requires docker-compose.

## Preparation

Install Docker Compose (Just google for it).

Build the images

    docker build -t jupyter/web:sshspawner web/
    docker build -t jupyter/app:sshspawner app/

Generate a key file

    mkdir config
    ssh-keygen -f config/newkey -N ''


## Bring up the containers

    docker-compose up -d


## Cleaning up and upgrading

In general a docker-compose up -d will refresh things.  Some times that isn't enough.  If all else fails, try...

    docker-compose stop
    docker-compose rm -f
