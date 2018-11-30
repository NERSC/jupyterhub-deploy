#!/bin/bash

# Get rid of any cert files older than 2 weeks

limit=14

find /certs -type f -name '*.key'           -mtime +$limit -exec rm {} \;
find /certs -type f -name '*.key-cert.pub'  -mtime +$limit -exec rm {} \;
find /certs -type f -name '*.key.pub'       -mtime +$limit -exec rm {} \;
