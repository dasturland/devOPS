#!/usr/bin/env sh
# Container entrypoint: wait for the database, migrate, then exec the CMD.
set -e

# ---------------------------------------------------------------------------
# Wait for PostgreSQL to accept connections (NFR-06).
# Only the host/port are referenced — never the credentials/environment dump.
# ---------------------------------------------------------------------------
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"

if [ "${WAIT_FOR_DB:-1}" = "1" ]; then
  echo "Waiting for database at ${DB_HOST}:${DB_PORT} ..."
  attempts=0
  until python -c "import socket,sys; s=socket.socket(); s.settimeout(2); sys.exit(0) if s.connect_ex(('${DB_HOST}', ${DB_PORT}))==0 else sys.exit(1)" 2>/dev/null; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 30 ]; then
      echo "Database not reachable after ${attempts} attempts; giving up." >&2
      exit 1
    fi
    sleep 2
  done
  echo "Database is up."
fi

# ---------------------------------------------------------------------------
# Apply migrations and (re)collect static assets.
# ---------------------------------------------------------------------------
echo "Applying migrations ..."
python manage.py migrate --noinput

echo "Collecting static files ..."
python manage.py collectstatic --noinput

# Hand off to the container command (gunicorn by default).
echo "Starting: $*"
exec "$@"
