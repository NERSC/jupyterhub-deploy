#!/bin/bash

docker build    \
    "$@"        \
    --tag registry.spin.nersc.gov/das/jupyter-off:latest .
