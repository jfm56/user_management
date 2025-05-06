#!/bin/bash
# Docker entrypoint script for User Management System
# This script runs initialization tasks before starting the application

set -e

echo "=== User Management System Docker Entrypoint ==="

# Run service initialization script if it exists
if [ -f "/myapp/scripts/init_services.sh" ]; then
    echo "Running service initialization..."
    /myapp/scripts/init_services.sh
else
    echo "Warning: Service initialization script not found, skipping"
fi

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec "$@"
