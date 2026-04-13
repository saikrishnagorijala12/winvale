#!/bin/sh

echo "Waiting for DB..."
./wait-for-db.sh

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 600