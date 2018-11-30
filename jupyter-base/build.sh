#!/bin/bash

branch=$(git symbolic-ref --short HEAD)

docker build    \
    --no-cache  \
    --tag registry.spin.nersc.gov/das/jupyter-base.$branch:latest .
