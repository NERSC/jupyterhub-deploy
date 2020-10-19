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

format=""
if [ "$imcmd" == "podman" ]; then
    format="--format docker"
fi

branch=$(git symbolic-ref --short HEAD)

# tag=registry.spin.nersc.gov/das/app-monitoring.jupyter-nersc-$branch:latest .
tag=registry.nersc.gov/m3384/app-monitoring.jupyter-nersc-$branch:latest

$imcmd build    \
    $format     \
    "$@"        \
    --tag $tag .
