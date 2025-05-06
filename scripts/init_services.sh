#!/bin/bash
# Script for initializing services for the User Management System
# This includes Kafka topic creation and other startup tasks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Create directories for scripts if they don't exist
mkdir -p "$SCRIPT_DIR"

echo "=== User Management System Service Initialization ==="

# Initialize Kafka topics
echo "Initializing Kafka topics..."

# Ensure the init_kafka_topics.sh script is executable
if [ -f "$PROJECT_DIR/init_kafka_topics.sh" ]; then
    chmod +x "$PROJECT_DIR/init_kafka_topics.sh"
    
    # Run in the background with a timeout to avoid hanging the startup
    timeout 60s "$PROJECT_DIR/init_kafka_topics.sh" &
    KAFKA_INIT_PID=$!
    
    # Wait for the Kafka initialization process to complete or timeout
    wait $KAFKA_INIT_PID || {
        if [ $? -eq 124 ]; then
            echo "Warning: Kafka topic initialization timed out but continuing startup"
        else
            echo "Warning: Kafka topic initialization failed with status $? but continuing startup"
        fi
    }
else
    echo "Warning: Kafka topic initialization script not found at $PROJECT_DIR/init_kafka_topics.sh"
    echo "Topics may need to be created manually."
fi

echo "=== Service initialization completed ==="
exit 0
