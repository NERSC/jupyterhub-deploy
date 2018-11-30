#!/bin/bash

service nslcd start

exec "$@"
