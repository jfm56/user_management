#!/bin/bash
set -e

# Wait for services to be ready
WAIT_TIMEOUT=${WAIT_TIMEOUT:-120}
MAX_RETRIES=30
REDIS_READY=false
KAFKA_READY=false

# Wait for Kafka (if enabled)
if [ "${ENABLE_KAFKA:-true}" = "true" ]; then
    echo "Waiting for Kafka to be ready..."
    RETRY_COUNT=0
    
    # Check if kafka-topics.sh is available
    if command -v kafka-topics.sh &> /dev/null; then
        function kafka_ready {
            kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092} --list 2>&1 > /dev/null
            return $?
        }
        
        while ! kafka_ready && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            echo "Waiting for Kafka to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
            sleep 2
            RETRY_COUNT=$((RETRY_COUNT+1))
        done
        
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Kafka is ready!"
            KAFKA_READY=true
        else
            echo "Warning: Kafka is not available after $MAX_RETRIES attempts. Celery worker might have limited functionality."
        fi
    else
        echo "Warning: kafka-topics.sh command not found. Assuming Kafka might not be available."
    fi
else
    echo "Kafka integration is disabled. Skipping Kafka check."
fi

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
RETRY_COUNT=0

if command -v redis-cli &> /dev/null; then
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping | grep -q "PONG"; then
            echo "Redis is ready!"
            REDIS_READY=true
            break
        else
            echo "Waiting for Redis to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
            sleep 2
            RETRY_COUNT=$((RETRY_COUNT+1))
        fi
    done
    
    if [ "$REDIS_READY" != "true" ]; then
        echo "Error: Redis is not available after $MAX_RETRIES attempts. Celery requires Redis to function properly."
        exit 1
    fi
else
    echo "Warning: redis-cli command not found. Cannot verify Redis connection."
    echo "Will attempt to start Celery worker anyway..."
fi

# Start Celery worker with appropriate settings
echo "Starting Celery worker..."
CONCURRENCY=${CELERY_CONCURRENCY:-4}
LOG_LEVEL=${CELERY_LOG_LEVEL:-info}

# Use the 'app' object in the celery_worker module
exec celery -A app.celery_worker:app worker --concurrency=$CONCURRENCY --loglevel=$LOG_LEVEL
