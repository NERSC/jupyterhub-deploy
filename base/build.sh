#!/bin/bash

branch=deploy-18-10
docker build --no-cache -t registry.spin.nersc.gov/das/jupyterhub-base.$branch:latest .
