#!/bin/bash
# Script to initialize Kafka topics for the User Management System
# This script ensures that all required Kafka topics exist

set -e

# Configuration
KAFKA_BROKER="kafka:29092"
REPLICATION_FACTOR=1
PARTITIONS=1
WAIT_TIME_SEC=5
MAX_RETRIES=12

# List of topics to create
TOPICS=(
    "user-email-notifications"
    "user-account-events"
    "user-role-changes"
    "user-verification-events"
)

echo "Waiting for Kafka to be ready..."

# Function to check if Kafka is ready
check_kafka() {
    kafka-topics --bootstrap-server $KAFKA_BROKER --list &>/dev/null
    return $?
}

# Wait for Kafka to be ready
retry_count=0
while ! check_kafka; do
    retry_count=$((retry_count+1))
    if [ $retry_count -ge $MAX_RETRIES ]; then
        echo "Error: Kafka not available after $MAX_RETRIES attempts. Exiting."
        exit 1
    fi
    echo "Kafka not yet ready. Waiting $WAIT_TIME_SEC seconds... (Attempt $retry_count/$MAX_RETRIES)"
    sleep $WAIT_TIME_SEC
done

echo "Kafka is ready. Creating topics..."

# Create topics if they don't exist
for topic in "${TOPICS[@]}"; do
    echo "Checking/creating topic: $topic"
    kafka-topics --bootstrap-server $KAFKA_BROKER --create --if-not-exists \
        --topic "$topic" --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS
done

echo "All Kafka topics created successfully!"
echo "List of available topics:"
kafka-topics --bootstrap-server $KAFKA_BROKER --list

exit 0
