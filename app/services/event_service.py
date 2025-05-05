"""
Event service for user management events.
This service provides a facade for publishing events to Kafka and handles fallbacks
when the Kafka service is not available.
"""

import logging
import importlib
from typing import Dict, Any, Optional, Type
from uuid import UUID

from app.models.user_model import User, UserRole

logger = logging.getLogger(__name__)

class EventService:
    """Service for publishing user-related events."""
    
    def __init__(self):
        """Initialize the event service."""
        self._kafka_producer = None
        
    @property
    def kafka_producer(self):
        """Lazy load the Kafka producer to avoid circular imports."""
        if self._kafka_producer is None:
            try:
                # Only import and initialize kafka when needed
                kafka_module = importlib.import_module('app.services.kafka_service')
                self._kafka_producer = kafka_module.kafka_producer
            except (ImportError, AttributeError) as e:
                logger.warning(f"Kafka producer not available: {e}. Events will not be published.")
                self._kafka_producer = None
        return self._kafka_producer
    
    def publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Publish an event to Kafka.
        
        Args:
            event_type: Type of event (defined in kafka_service.EventTypes)
            data: Event data
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            logger.warning(f"Kafka producer not available. Event {event_type} not published.")
            return False
            
        try:
            return self.kafka_producer.publish_event(event_type, data)
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False
    
    def publish_account_verification_event(self, user: User) -> bool:
        """
        Publish an account verification event.
        
        Args:
            user: User object
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname,
                "verification_token": user.verification_token
            }
            
            return self.publish_event(
                EventTypes.VERIFICATION_EVENT,
                {
                    "subtype": "email_verification",
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish account verification event: {e}")
            return False
    
    def publish_account_locked_event(self, user: User) -> bool:
        """
        Publish an account locked event.
        
        Args:
            user: User object
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname
            }
            
            return self.publish_event(
                EventTypes.ACCOUNT_EVENT,
                {
                    "subtype": "account_locked",
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish account locked event: {e}")
            return False
    
    def publish_account_unlocked_event(self, user: User) -> bool:
        """
        Publish an account unlocked event.
        
        Args:
            user: User object
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname
            }
            
            return self.publish_event(
                EventTypes.ACCOUNT_EVENT,
                {
                    "subtype": "account_unlocked",
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish account unlocked event: {e}")
            return False
    
    def publish_role_change_event(self, user: User, old_role: UserRole) -> bool:
        """
        Publish a role change event.
        
        Args:
            user: User object
            old_role: Previous role
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname,
                "old_role": str(old_role),
                "new_role": str(user.role)
            }
            
            return self.publish_event(
                EventTypes.ROLE_CHANGE,
                {
                    "subtype": "role_upgrade",
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish role change event: {e}")
            return False
    
    def publish_professional_status_event(self, user: User) -> bool:
        """
        Publish a professional status event.
        
        Args:
            user: User object
            
        Returns:
            bool: True if event was published, False otherwise
        """
        if not self.kafka_producer:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname
            }
            
            return self.publish_event(
                EventTypes.EMAIL_NOTIFICATION,
                {
                    "subtype": "professional_status",
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish professional status event: {e}")
            return False

# Create a singleton instance
event_service = EventService()
