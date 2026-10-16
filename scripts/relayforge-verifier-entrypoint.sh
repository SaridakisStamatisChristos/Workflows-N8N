#!/bin/sh
set -eu

PG_BINDIR="$(dirname "$(find /usr/lib/postgresql -path '*/bin/initdb' -type f | sort -V | tail -n 1)")"
if [ -z "$PG_BINDIR" ] || [ ! -x "$PG_BINDIR/initdb" ]; then
  echo "PostgreSQL binaries are unavailable in verifier image" >&2
  exit 70
fi

mkdir -p /tmp/pgdata /tmp/pgsocket /tmp/pg-home /tmp/home /tmp/cache
chown -R postgres:postgres /tmp/pgdata /tmp/pgsocket /tmp/pg-home

if [ ! -s /tmp/pgdata/PG_VERSION ]; then
  runuser -u postgres -- env HOME=/tmp/pg-home "$PG_BINDIR/initdb" \
    -D /tmp/pgdata --auth=trust --username=postgres >/tmp/initdb.log
fi

runuser -u postgres -- env HOME=/tmp/pg-home "$PG_BINDIR/pg_ctl" \
  -D /tmp/pgdata -o "-k /tmp/pgsocket -h ''" -w start >/tmp/pg-start.log
runuser -u postgres -- "$PG_BINDIR/createdb" -h /tmp/pgsocket -U postgres relayforge 2>/dev/null || true

export DATABASE_URL='postgresql://postgres@localhost/relayforge?host=%2Ftmp%2Fpgsocket'
export PGHOST=/tmp/pgsocket
export PGUSER=postgres
export PGDATABASE=relayforge
export HOME=/tmp/home
export XDG_CACHE_HOME=/tmp/cache
export CI=true

# Bootstrap requires only CHOWN/SETUID/SETGID. Drop every capability before any
# target-repository verification command executes.
exec setpriv --bounding-set=-all --inh-caps=-all --ambient-caps=-all -- "$@"
