#!/bin/bash
# Kafka initialization script that will be run outside the FastAPI container
# This script will create required Kafka topics if they don't exist

set -e

echo "=== Kafka Topic Initialization ==="

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
max_retries=30
counter=0
while ! docker compose exec -T kafka bash -c "kafka-topics --bootstrap-server kafka:29092 --list" > /dev/null 2>&1; do
    sleep 2
    counter=$((counter+1))
    echo "Waiting for Kafka to be ready... Attempt $counter of $max_retries"
    if [ $counter -eq $max_retries ]; then
        echo "Error: Kafka did not become ready in time."
        exit 1
    fi
done

echo "Kafka is ready. Creating topics..."

# Topics to create
topics=(
    "user-email-notifications"
    "user-account-events"
    "user-role-changes"
    "user-verification-events"
)

# Create each topic
for topic in "${topics[@]}"; do
    echo "Creating topic: $topic"
    docker compose exec -T kafka kafka-topics --create --if-not-exists \
        --bootstrap-server kafka:29092 \
        --replication-factor 1 \
        --partitions 1 \
        --topic "$topic"
done

echo "Verifying created topics:"
docker compose exec -T kafka kafka-topics --list --bootstrap-server kafka:29092

echo "=== Kafka Topic Initialization Complete ==="
