#!/bin/bash

branch=$(git symbolic-ref --short HEAD)

docker build    \
    "$@"        \
    --tag registry.spin.nersc.gov/das/jupyter-nersc-mods.$branch:latest .
