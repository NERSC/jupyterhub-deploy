#!/usr/bin/env python

# Script to kill stale jupyterhub-singleuser processes. Looks for notebook
# processes owned by a user and kills all but the latest one

import subprocess
from collections import defaultdict

import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--username", help='username for processes to kill')
args = parser.parse_args()


if args.username:
    output = subprocess.check_output("ps -u %s --sort=start_time ux | grep 'jupyterhub-singleuser' | grep -v grep | awk '{print $1, $2}'" % args.username, shell=True)
else:
    output = subprocess.check_output("ps --sort=start_time aux | grep 'jupyterhub-singleuser' | grep -v grep | awk '{print $1, $2}'", shell=True)
proc_table = defaultdict(list)

output = output.strip().split('\n')
for line in output:
    if line.strip():
        user, proc = line.split()
        proc_table[user].append(proc)

for key,val in proc_table.iteritems():
    target_procs = val[:-1]
    print("Killing processes for %s: %s" % (key, str(target_procs)))
    for p in target_procs:
        subprocess.call("kill %s" % p, shell=True)
