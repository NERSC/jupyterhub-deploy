#!/usr/bin/env bash


nohup /global/common/cori/software/python/3.5-anaconda/bin/jupyterhub-singleuser $@ &

pid=$!
echo $pid
