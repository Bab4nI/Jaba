#!/bin/sh

until pg_isready -h db -U postgres -d netlabai; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "PostgreSQL is ready - executing command"
exec "$@"