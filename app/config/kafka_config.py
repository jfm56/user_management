"""
Configuration module for Kafka settings.
"""
import os
from typing import Dict

# Kafka connection settings
kafka_bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

# Kafka topic configuration
kafka_topics: Dict[str, str] = {
    'email_notifications': 'user-email-notifications',
    'account_events': 'user-account-events',
    'role_changes': 'user-role-changes',
    'verification_events': 'user-verification-events',
}

# Producer configuration
producer_config = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'client.id': 'user-management-producer',
    'acks': 'all',  # Wait for all replicas to acknowledge
}

# Consumer configuration
consumer_config = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': 'user-management-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'session.timeout.ms': 30000,
    'heartbeat.interval.ms': 10000,
}

# Topic configurations
default_topic_config = {
    'partitions': 3,
    'replication_factor': 1,
}
