# email_service.py
from builtins import ValueError, dict, str
import logging
import importlib
import json
from uuid import UUID
from typing import Optional, Union, Dict, Any

from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager
        # Lazily import kafka_service to avoid circular imports
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
                logger.warning(f"Kafka producer not available: {e}. Will use direct email sending.")
                self._kafka_producer = None
        return self._kafka_producer
    
    def _publish_email_event(self, event_subtype: str, user_data: Dict[str, Any]) -> bool:
        """Publish an email event to Kafka.
        
        Args:
            event_subtype: The subtype of email event ('verification_email', 'account_locked', etc.)
            user_data: User data to be included in the event
            
        Returns:
            bool: True if event was published successfully, False otherwise
        """
        if self._kafka_producer is None:
            return False
            
        try:
            from app.services.kafka_service import EventTypes
            return self._kafka_producer.publish_event(
                EventTypes.EMAIL_NOTIFICATION,
                {
                    "subtype": event_subtype,
                    "user_data": user_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish email event: {e}")
            return False
    
    def send_user_email(self, recipient: Union[User, Dict], subject: str, content: str, content_type: str = "html"):
        """Send an email to a user.
        
        Args:
            recipient: User object or dictionary with email and name
            subject: Email subject
            content: Email content
            content_type: Content type (html or text)
        """
        if isinstance(recipient, User):
            recipient_email = recipient.email
            recipient_name = recipient.nickname or recipient.first_name or "User"
        else:
            recipient_email = recipient.get("email")
            recipient_name = recipient.get("name") or recipient.get("nickname") or "User"
            
        if not recipient_email:
            raise ValueError("Recipient email is required")
            
        try:
            if content_type == "html":
                self.smtp_client.send_email(subject, content, recipient_email)
            else:
                self.smtp_client.send_text_email(subject, content, recipient_email)
                
            logger.info(f"Email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False

    async def send_user_email_async(self, user_data: dict, email_type: str):
        """Send an email to a user (backward compatibility method)."""
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification"
        }

        if email_type not in subject_map:
            raise ValueError("Invalid email type")

        html_content = self.template_manager.render_template(email_type, **user_data)
        
        # Publish email event (non-blocking) then send directly
        self._publish_email_event('verification_email', user_data)
        self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])
        return True

    async def send_verification_email(self, user: User):
        """Send a verification email to a user.
        
        Args:
            user: User object with email and verification_token
        """
        if not user.verification_token:
            raise ValueError("User does not have a verification token set.")

        verification_url = f"{settings.server_base_url.rstrip('/')}/verify-email/{user.id}/{user.verification_token}"
    
        logger.info(f"Sending verification email to {user.email} with link: {verification_url}")
        
        # Prepare user data for the event
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "nickname": user.nickname or user.first_name or "User",
            "verification_token": user.verification_token,
            "verification_url": verification_url
        }
        
        # Publish event and always send verification email directly
        self._publish_email_event('verification_email', user_data)
        await self.send_user_email_async(
            {
                "name": user.first_name or user.nickname or "User",
                "verification_url": verification_url,
                "email": user.email
            },
            email_type='email_verification'
        )
