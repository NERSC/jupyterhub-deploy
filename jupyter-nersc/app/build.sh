#!/bin/bash

branch=$(git symbolic-ref --short HEAD)

docker build                    \
    --build-arg branch=$branch  \
    --no-cache                  \
    --tag registry.spin.nersc.gov/das/jupyter-nersc-app.$branch:latest .
