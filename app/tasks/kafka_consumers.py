import json
import logging
import threading
import time
import importlib
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable, List, Optional, Union

from confluent_kafka import Consumer, KafkaException, KafkaError
from celery import Celery

from app.config.celery_config import kafka_bootstrap_servers, kafka_topics
from app.services.kafka_service import EventTypes
from app.celery_worker import app as celery_app
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_account_unlocked_email,
    send_role_upgrade_email,
    send_professional_status_email
)

logger = logging.getLogger(__name__)


class KafkaEventConsumer:
    """Consumer for processing events from Kafka topics."""
    
    def __init__(self, group_id="user-management-consumer", poll_timeout=1.0):
        """Initialize the Kafka consumer with configuration.
        
        Args:
            group_id (str): Consumer group ID to use
            poll_timeout (float): Timeout in seconds for message polling
        """
        self.config = {
            'bootstrap.servers': kafka_bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # We'll commit manually after processing
            'session.timeout.ms': 30000,  # 30 seconds
            'heartbeat.interval.ms': 10000,  # 10 seconds
        }
        self.consumer = None  # Will be initialized in start()
        self.topics = kafka_topics
        self.running = False
        self.consumer_thread = None
        self.poll_timeout = poll_timeout
        self.shutdown_event = threading.Event()
        
    def _setup_handlers(self) -> Dict[str, Dict[str, Callable]]:
        """Set up event handlers for each topic and event type."""
        return {
            self.topics['email_notifications']: {
                'verification_email': lambda data: send_verification_email.delay(user_data=data),
                'account_locked': lambda data: send_account_locked_email.delay(user_data=data),
                'account_unlocked': lambda data: send_account_unlocked_email.delay(user_data=data),
                'role_upgrade': lambda data: send_role_upgrade_email.delay(user_data=data),
                'professional_status': lambda data: send_professional_status_email.delay(user_data=data),
            },
            self.topics['account_events']: {
                'account_locked': lambda data: send_account_locked_email.delay(user_data=data),
                'account_unlocked': lambda data: send_account_unlocked_email.delay(user_data=data),
            },
            self.topics['role_changes']: {
                'role_upgrade': lambda data: send_role_upgrade_email.delay(user_data=data),
            },
            self.topics['verification_events']: {
                'email_verification': lambda data: send_verification_email.delay(user_data=data),
            }
        }
    
    def start(self):
        """Start the Kafka consumer in a separate thread."""
        if self.running:
            logger.warning("Consumer is already running")
            return
            
        logger.info("Starting Kafka consumer...")
        self.consumer = Consumer(self.config)
        self.handlers = self._setup_handlers()
        
        # Subscribe to all topics
        topics_to_subscribe = list(self.topics.values())
        logger.info(f"Subscribing to Kafka topics: {topics_to_subscribe}")
        self.consumer.subscribe(topics_to_subscribe)
        
        # Start consumer thread
        self.running = True
        self.shutdown_event.clear()
        self.consumer_thread = threading.Thread(target=self._consume_loop)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        
        logger.info("Kafka consumer started successfully")
        
    def stop(self):
        """Stop the Kafka consumer."""
        if not self.running:
            logger.warning("Consumer is not running")
            return
            
        logger.info("Stopping Kafka consumer...")
        self.running = False
        self.shutdown_event.set()
        
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0)
            
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            
        logger.info("Kafka consumer stopped successfully")
    
    def _consume_loop(self):
        """Main consumer loop that runs in a separate thread."""
        try:
            while self.running and not self.shutdown_event.is_set():
                try:
                    # Poll for messages
                    message = self.consumer.poll(self.poll_timeout)
                    
                    if message is None:
                        continue
                        
                    # Process message
                    self._process_message(message)
                    
                except KafkaException as ke:
                    logger.error(f"Kafka error in consume loop: {ke}")
                    if not self.running:
                        break
                    time.sleep(1)  # Avoid tight loop on error
                    
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consume loop: {e}")
        finally:
            logger.info("Exiting Kafka consume loop")
            if self.consumer:
                self.consumer.close()
    
    def _process_message(self, message):
        """Process a Kafka message and route it to the appropriate handler.
        
        Args:
            message: Kafka message object
        """
        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                # End of partition, not an error
                logger.debug(f"Reached end of partition: {message.topic()}/{message.partition()}")
            else:
                logger.error(f"Consumer error: {message.error()}")
            return
        
        try:
            # Parse the message value as JSON
            value_bytes = message.value()
            if not value_bytes:
                logger.warning("Received message with empty value")
                self.consumer.commit(message)
                return
                
            value_str = value_bytes.decode('utf-8')
            data = json.loads(value_str)
            
            # Extract event metadata
            event_type = data.get('event_type')
            subtype = data.get('payload', {}).get('subtype')
            user_data = data.get('payload', {}).get('user_data', {})
            
            if not event_type or not subtype or not user_data:
                logger.error(f"Invalid message format: {data}")
                self.consumer.commit(message)
                return
            
            # Route to the appropriate handler based on topic and event subtype
            topic = message.topic()
            
            logger.info(f"Processing {event_type}/{subtype} event from topic: {topic}")
            
            # Find handler for this topic and subtype
            if topic in self.handlers and subtype in self.handlers[topic]:
                handler = self.handlers[topic][subtype]
                handler(user_data)
                logger.info(f"Successfully processed {event_type}/{subtype} event")
            else:
                logger.warning(f"No handler found for event: {event_type}/{subtype} from topic: {topic}")
            
            # Commit the offset after processing
            self.consumer.commit(message)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
            self.consumer.commit(message)  # Still commit to avoid reprocessing
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Don't commit on processing errors to allow retry


# Global consumer instance
kafka_consumer = KafkaEventConsumer()


def start_kafka_consumers():
    """Start Kafka consumers for processing events."""
    try:
        logger.info("Starting Kafka consumer service")
        kafka_consumer.start()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            kafka_consumer.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Kafka consumer service started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer service: {e}")
        return False


def stop_kafka_consumers():
    """Stop all Kafka consumers."""
    try:
        logger.info("Stopping Kafka consumer service")
        kafka_consumer.stop()
        logger.info("Kafka consumer service stopped successfully")
        return True
    except Exception as e:
        logger.error(f"Error stopping Kafka consumer service: {e}")
        return False
    
    def start(self, poll_timeout=1.0):
        """Start consuming messages from Kafka topics."""
        self.running = True
        
        logger.info("Starting Kafka consumer...")
        
        try:
            while self.running:
                message = self.consumer.poll(poll_timeout)
                if message:
                    self.process_message(message)
        except KeyboardInterrupt:
            logger.info("Stopping Kafka consumer...")
        finally:
            self.consumer.close()
            self.running = False
    
    def stop(self):
        """Stop consuming messages from Kafka topics."""
        self.running = False

class KafkaConsumerThread(threading.Thread):
    """Thread for running a Kafka consumer in the background."""
    
    def __init__(self, group_id="user-management-consumer"):
        """Initialize the thread."""
        super().__init__()
        self.daemon = True  # Make the thread a daemon so it stops when the main program stops
        self.consumer = KafkaEventConsumer(group_id=group_id)
        
    def run(self):
        """Run the consumer thread."""
        self.consumer.subscribe()
        self.consumer.start()
    
    def stop(self):
        """Stop the consumer thread."""
        self.consumer.stop()
        self.join()

# Function to start the Kafka consumer in a separate thread
def start_kafka_consumer():
    """Start the Kafka consumer in a separate thread."""
    consumer_thread = KafkaConsumerThread()
    consumer_thread.start()
    return consumer_thread
