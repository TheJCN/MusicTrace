#!/bin/sh
set -e

if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "Applying migrations..."
  python manage.py migrate --noinput

  echo "Collecting static..."
  python manage.py collectstatic --noinput
fi

exec "$@"
