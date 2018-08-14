#!/bin/bash

# Get rid of any certs older than 2 weeks

find /certs -type f -name 'x509_*' -mtime +14 -exec rm {} \;
