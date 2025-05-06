#!/bin/bash
# Master startup script for the User Management System
# This script ensures Kafka topics are properly created before starting all services

set -e

echo "=== Starting User Management System ==="

# Check if docker and docker compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed or not in PATH"
    exit 1
fi

# Step 1: Ensure Zookeeper and Kafka are started first
echo "Starting Zookeeper and Kafka..."
docker compose up -d zookeeper kafka

# Step 2: Wait for Kafka to be ready
echo "Waiting for Kafka to initialize..."
sleep 10

# Step 3: Initialize Kafka topics
echo "Creating Kafka topics..."
./kafka-init.sh

# Step 4: Start the remaining services
echo "Starting all other services..."
docker compose up -d

echo "=== User Management System Started ==="
echo ""
echo "Services available at:"
echo "- API: http://localhost:8000/docs"
echo "- Admin Panel: http://localhost:8000/admin"
echo "- pgAdmin: http://localhost:5050"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker compose down"
echo ""
echo "Note: 401 authentication errors may still appear as 500 errors due to a known issue that is being addressed."
