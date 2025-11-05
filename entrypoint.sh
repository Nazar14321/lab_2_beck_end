#!/usr/bin/env bash
set -euo pipefail


retries=12
until flask --app app db upgrade >/dev/null 2>&1 || [ $retries -le 0 ]; do
  echo "DB not ready yet, retrying..."
  retries=$((retries-1))
  sleep 2
done


echo "Running migrations..."
flask --app app db upgrade

if [ "${RUN_SEED:-0}" = "1" ]; then
  echo "Seeding..."
  flask --app app seed
fi


exec gunicorn -w 2 -k gthread -b 0.0.0.0:${PORT:-6060} app:app