#!/bin/bash

imcmd=""
for command in docker podman; do
    if [ $(command -v $command) ]; then
        imcmd=$command
        break
    fi
done
if [ -n "$imcmd" ]; then
    echo "Using $imcmd"
else
    echo "No image command defined"
    exit 1
fi

branch=$(git symbolic-ref --short HEAD)

$imcmd build    \
    "$@"
    --tag registry.spin.nersc.gov/das/jupyter-base-$branch:latest .
