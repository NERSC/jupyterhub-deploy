#!/bin/bash

branch=deploy-18-10

docker build                    \
    --build-arg branch=$branch  \
    --no-cache                  \
    --tag registry.spin.nersc.gov/das/jupyterhub-jupyter-dev.$branch:latest .
