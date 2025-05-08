import logging
try:
    from celery import shared_task
    from app.celery_worker import app as celery
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    celery = None
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

logger = logging.getLogger(__name__)

# Create a singleton instance of the template manager and email service
template_manager = TemplateManager()
email_service = EmailService(template_manager=template_manager)

@shared_task(
    name="send_verification_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60  # 60 seconds
)
def send_verification_email(self, user_data):
    """
    Task to send a verification email.
    
    Args:
        user_data: Dictionary containing user data including id, email, and verification_token
    """
    try:
        logger.info(f"Sending verification email to {user_data['email']}")
        
        # Create a User object from the data
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            nickname=user_data.get('nickname', 'User'),
            verification_token=user_data['verification_token']
        )
        
        # Send the verification email
        email_service.send_verification_email(user)
        
        logger.info(f"Verification email sent to {user_data['email']}")
        return f"Verification email sent to {user_data['email']}"
        
    except Exception as exc:
        logger.error(f"Error sending verification email: {exc}")
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=self.default_retry_delay * (2 ** self.request.retries))

@shared_task(
    name="send_account_locked_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_account_locked_email(self, user_data):
    """
    Task to send an account locked notification.
    
    Args:
        user_data: Dictionary containing user data including email
    """
    try:
        logger.info(f"Sending account locked email to {user_data['email']}")
        
        # Create a User object from the data
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            nickname=user_data.get('nickname', 'User')
        )
        
        # Send the account locked email
        email_service.send_user_email(
            recipient=user,
            subject="Account Locked - Security Alert",
            content=f"Dear {user.nickname},\n\nYour account has been locked due to multiple failed login attempts. Please contact support to unlock your account.",
            content_type="text"
        )
        
        logger.info(f"Account locked email sent to {user_data['email']}")
        return f"Account locked email sent to {user_data['email']}"
        
    except Exception as exc:
        logger.error(f"Error sending account locked email: {exc}")
        self.retry(exc=exc, countdown=self.default_retry_delay * (2 ** self.request.retries))

@shared_task(
    name="send_account_unlocked_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_account_unlocked_email(self, user_data):
    """
    Task to send an account unlocked notification.
    
    Args:
        user_data: Dictionary containing user data including email
    """
    try:
        logger.info(f"Sending account unlocked email to {user_data['email']}")
        
        # Create a User object from the data
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            nickname=user_data.get('nickname', 'User')
        )
        
        # Send the account unlocked email
        email_service.send_user_email(
            recipient=user,
            subject="Account Unlocked - Access Restored",
            content=f"Dear {user.nickname},\n\nYour account has been unlocked. You can now login to your account.",
            content_type="text"
        )
        
        logger.info(f"Account unlocked email sent to {user_data['email']}")
        return f"Account unlocked email sent to {user_data['email']}"
        
    except Exception as exc:
        logger.error(f"Error sending account unlocked email: {exc}")
        self.retry(exc=exc, countdown=self.default_retry_delay * (2 ** self.request.retries))

@shared_task(
    name="send_role_upgrade_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_role_upgrade_email(self, user_data):
    """
    Task to send a role upgrade notification.
    
    Args:
        user_data: Dictionary containing user data including email, old_role, new_role
    """
    try:
        logger.info(f"Sending role upgrade email to {user_data['email']}")
        
        # Create a User object from the data
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            nickname=user_data.get('nickname', 'User'),
            role=user_data['new_role']
        )
        
        old_role = user_data['old_role']
        new_role = user_data['new_role']
        
        # Send the role upgrade email
        email_service.send_user_email(
            recipient=user,
            subject="Account Role Upgraded",
            content=f"Dear {user.nickname},\n\nYour account role has been upgraded from {old_role} to {new_role}. You now have access to additional features.",
            content_type="text"
        )
        
        logger.info(f"Role upgrade email sent to {user_data['email']}")
        return f"Role upgrade email sent to {user_data['email']}"
        
    except Exception as exc:
        logger.error(f"Error sending role upgrade email: {exc}")
        self.retry(exc=exc, countdown=self.default_retry_delay * (2 ** self.request.retries))

@shared_task(
    name="send_professional_status_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_professional_status_email(self, user_data):
    """
    Task to send a professional status upgrade notification.
    
    Args:
        user_data: Dictionary containing user data including email
    """
    try:
        logger.info(f"Sending professional status email to {user_data['email']}")
        
        # Create a User object from the data
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            nickname=user_data.get('nickname', 'User'),
            is_professional=True
        )
        
        # Send the professional status email
        email_service.send_user_email(
            recipient=user,
            subject="Professional Status Activated",
            content=f"Dear {user.nickname},\n\nCongratulations! Your account has been upgraded to Professional status. You now have access to premium features.",
            content_type="text"
        )
        
        logger.info(f"Professional status email sent to {user_data['email']}")
        return f"Professional status email sent to {user_data['email']}"
        
    except Exception as exc:
        logger.error(f"Error sending professional status email: {exc}")
        self.retry(exc=exc, countdown=self.default_retry_delay * (2 ** self.request.retries))
