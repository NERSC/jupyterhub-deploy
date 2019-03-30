#!/bin/bash

branch=$(git symbolic-ref --short HEAD)

docker build                    \
    --build-arg branch=$branch  \
    "$@"                        \
    --tag registry.spin.nersc.gov/das/web-jupyterhub.jupyter-nersc-$branch:latest .
