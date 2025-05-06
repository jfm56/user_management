#!/bin/bash
set -e

# Wait for Kafka to be ready (if enabled)
if [ "${ENABLE_KAFKA:-true}" = "true" ]; then
    echo "Waiting for Kafka to be ready..."
    
    # Check if kafka-topics command is available
    if command -v kafka-topics &> /dev/null; then
        function kafka_ready {
            kafka-topics --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092} --list 2>&1 > /dev/null
            return $?
        }
        
        KAFKA_CONNECT_RETRIES=${KAFKA_CONNECT_RETRIES:-30}
        RETRY_COUNT=0
        
        while ! kafka_ready && [ $RETRY_COUNT -lt $KAFKA_CONNECT_RETRIES ]; do
            echo "Waiting for Kafka to be ready... (Attempt $((RETRY_COUNT+1))/$KAFKA_CONNECT_RETRIES)"
            sleep 2
            RETRY_COUNT=$((RETRY_COUNT+1))
        done
        
        if [ $RETRY_COUNT -lt $KAFKA_CONNECT_RETRIES ]; then
            echo "Kafka is ready!"
            
            # Set up Kafka topics
            echo "Setting up Kafka topics..."
            TOPICS=("user-email-notifications" "user-account-events" "user-role-changes" "user-verification-events")
            
            for TOPIC in "${TOPICS[@]}"; do
                echo "Creating topic: $TOPIC"
                kafka-topics --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092} \
                    --create --if-not-exists \
                    --topic $TOPIC \
                    --partitions ${KAFKA_TOPIC_PARTITIONS:-1} \
                    --replication-factor ${KAFKA_REPLICATION_FACTOR:-1} || {
                    echo "Warning: Failed to create Kafka topic $TOPIC, continuing anyway"
                }
            done
            
            # List created topics for verification
            echo "Available Kafka topics:"
            kafka-topics --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092} --list
        else
            echo "Warning: Kafka is not available after $KAFKA_CONNECT_RETRIES attempts. Continuing without Kafka."
        fi
    else
        echo "Warning: kafka-topics command not found. Trying to use init_kafka_topics.sh script..."
        
        # Try to run the dedicated Kafka init script if it exists
        if [ -f "/myapp/init_kafka_topics.sh" ] && [ -x "/myapp/init_kafka_topics.sh" ]; then
            echo "Running init_kafka_topics.sh script..."
            /myapp/init_kafka_topics.sh
        else
            echo "Warning: Neither kafka-topics command nor init_kafka_topics.sh script found. Skipping Kafka topic creation."
        fi
    fi
else
    echo "Kafka integration is disabled. Skipping Kafka setup."
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --no-server-header --log-level debug
