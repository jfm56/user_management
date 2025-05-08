import json
import logging
from typing import Any, Dict

try:
    from confluent_kafka import Producer
except ImportError:
    class Producer:
        def __init__(self, *args, **kwargs):
            pass
        def produce(self, *args, **kwargs):
            pass
        def flush(self):
            pass

from app.config.celery_config import kafka_bootstrap_servers, kafka_topics

logger = logging.getLogger(__name__)

class KafkaProducer:
    """Service for publishing events to Kafka topics."""
    
    def __init__(self):
        """Initialize the Kafka producer with configuration."""
        self.config = {
            'bootstrap.servers': kafka_bootstrap_servers,
            'client.id': 'user-management-producer',
            'acks': 'all',  # Wait for all replicas to acknowledge
        }
        self.producer = Producer(self.config)
        self.topics = kafka_topics
    
    def _delivery_report(self, err, msg):
        """Callback function for message delivery reports."""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Publish an event to the appropriate Kafka topic.
        
        Args:
            event_type: Type of event (e.g., 'email_notifications', 'account_events')
            data: The event data to be published
            
        Returns:
            bool: True if the message was successfully queued for publishing
        """
        if event_type not in self.topics:
            logger.error(f"Unknown event type: {event_type}")
            return False
        
        topic = self.topics[event_type]
        
        try:
            # Add metadata to the event
            event_data = {
                "event_type": event_type,
                "payload": data
            }
            
            # Convert dict to JSON string
            message = json.dumps(event_data).encode('utf-8')
            
            # Produce the message to Kafka
            self.producer.produce(
                topic=topic,
                value=message,
                callback=self._delivery_report
            )
            
            # Flush to ensure the message is sent immediately
            # For higher throughput scenarios, you might want to batch messages
            self.producer.flush()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to publish event to Kafka: {e}")
            return False

# Global instance that can be imported and used throughout the application
kafka_producer = KafkaProducer()

# Event type constants
class EventTypes:
    EMAIL_NOTIFICATION = "email_notifications"
    ACCOUNT_EVENT = "account_events"
    ROLE_CHANGE = "role_changes"
    VERIFICATION_EVENT = "verification_events"
