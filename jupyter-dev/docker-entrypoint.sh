#!/bin/bash

# file_env VAR [DEFAULT]
# ----------------------
# Treat the value of VAR_FILE as the path to a secrets file and initialize VAR
# with the contents of that file.  From postgres docker-entrypoint.sh.

file_env() {
    local var="$1"
    local fileVar="${var}_FILE"
    local def="${2:-}"
    if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
        echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
        exit 1
    fi
    local val="$def"
    if [ "${!var:-}" ]; then
        val="${!var}"
    elif [ "${!fileVar:-}" ]; then
        val="$(< "${!fileVar}")"
    fi
    export "$var"="$val"
    unset "$fileVar"
}

file_env 'POSTGRES_PASSWORD'
file_env 'SKEY'

exec "$@"
