#!/bin/bash

branch=$(git symbolic-ref --short HEAD)
docker build --no-cache -t registry.spin.nersc.gov/das/jupyterhub-base.$branch:latest .
