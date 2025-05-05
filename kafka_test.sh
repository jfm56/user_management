#!/bin/bash
# Kafka testing utility script

# Set default Kafka bootstrap server
KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092}

# Command-line argument parsing
ACTION=$1
TOPIC=$2
MESSAGE=$3

# Function to show usage information
show_usage() {
    echo "Kafka Testing Utility"
    echo "Usage: $0 <action> [topic] [message]"
    echo ""
    echo "Actions:"
    echo "  list                       - List all Kafka topics"
    echo "  consume <topic>            - Consume messages from a topic"
    echo "  produce <topic> <message>  - Produce a message to a topic"
    echo "  test <topic>               - Send a test message to a topic"
    echo "  help                       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 consume user-email-notifications"
    echo "  $0 produce user-email-notifications '{\"event_type\":\"email_notification\",\"payload\":{\"subtype\":\"verification_email\",\"user_data\":{\"id\":\"123\",\"email\":\"test@example.com\",\"nickname\":\"testuser\"}}}'"
    echo "  $0 test user-email-notifications"
    echo ""
}

# Function to list topics
list_topics() {
    echo "Listing Kafka topics..."
    if command -v kafkacat &> /dev/null; then
        kafkacat -b $KAFKA_BOOTSTRAP_SERVERS -L | grep topic
    elif command -v kafka-topics.sh &> /dev/null; then
        kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --list
    else
        echo "Error: Neither kafkacat nor kafka-topics.sh found."
        exit 1
    fi
}

# Function to consume messages from a topic
consume_topic() {
    if [ -z "$TOPIC" ]; then
        echo "Error: Topic name is required for consume action."
        show_usage
        exit 1
    fi
    
    echo "Consuming messages from topic $TOPIC..."
    if command -v kafkacat &> /dev/null; then
        kafkacat -b $KAFKA_BOOTSTRAP_SERVERS -C -t $TOPIC -f 'Offset: %o\nKey: %k\nValue: %s\nTimestamp: %T\n--\n'
    else
        echo "Error: kafkacat not found. Please install it to consume messages."
        exit 1
    fi
}

# Function to produce a message to a topic
produce_message() {
    if [ -z "$TOPIC" ] || [ -z "$MESSAGE" ]; then
        echo "Error: Topic and message are required for produce action."
        show_usage
        exit 1
    fi
    
    echo "Producing message to topic $TOPIC..."
    if command -v kafkacat &> /dev/null; then
        echo "$MESSAGE" | kafkacat -b $KAFKA_BOOTSTRAP_SERVERS -P -t $TOPIC
        echo "Message sent."
    else
        echo "Error: kafkacat not found. Please install it to produce messages."
        exit 1
    fi
}

# Function to send a test message to a topic
send_test_message() {
    if [ -z "$TOPIC" ]; then
        echo "Error: Topic name is required for test action."
        show_usage
        exit 1
    fi
    
    # Generate a test message
    TEST_ID=$(date +%s)
    TEST_MESSAGE="{\"event_type\":\"email_notification\",\"payload\":{\"subtype\":\"verification_email\",\"user_data\":{\"id\":\"test-$TEST_ID\",\"email\":\"test-$TEST_ID@example.com\",\"nickname\":\"TestUser\",\"verification_token\":\"test-token-$TEST_ID\"}}}"
    
    echo "Sending test message to topic $TOPIC..."
    if command -v kafkacat &> /dev/null; then
        echo "$TEST_MESSAGE" | kafkacat -b $KAFKA_BOOTSTRAP_SERVERS -P -t $TOPIC
        echo "Test message sent. Test ID: $TEST_ID"
    else
        echo "Error: kafkacat not found. Please install it to send test messages."
        exit 1
    fi
}

# Main logic
case $ACTION in
    list)
        list_topics
        ;;
    consume)
        consume_topic
        ;;
    produce)
        produce_message
        ;;
    test)
        send_test_message
        ;;
    help|"")
        show_usage
        ;;
    *)
        echo "Error: Unknown action: $ACTION"
        show_usage
        exit 1
        ;;
esac

exit 0
