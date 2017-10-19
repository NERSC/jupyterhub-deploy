#!/bin/bash

echo "";
echo "Running initdb.sh.";
if [ -z "$JPY_PSQL_PASSWORD" ]; then
    echo "Need to set JPY_PSQL_PASSWORD in Dockerfile or via command line.";
    exit 1;
fi
echo "";

# Start a postgres daemon, ignoring log output.
# gosu postgres pg_ctl start -w -l /dev/null

# Create a Jupyterhub user and database.
psql --user postgres -c "CREATE DATABASE jupyterhub;"
psql --user postgres -c "CREATE USER jupyterhub WITH ENCRYPTED PASSWORD '$JPY_PSQL_PASSWORD';"
psql --user postgres -c "GRANT ALL PRIVILEGES ON DATABASE jupyterhub TO jupyterhub;"

# Alter pg_hba.conf to actually require passwords.  The default image exposes
# allows any user to connect without requiring a password, which is a liability
# if this is run forwarding ports from the host machine.
sed -ri -e 's/(host all all all )(trust)/\1md5/' "$PGDATA"/pg_hba.conf

# Stop the daemon.  The root Dockerfile will restart the server for us.
# gosu postgres pg_ctl stop -w
