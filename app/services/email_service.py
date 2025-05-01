# email_service.py
from builtins import ValueError, dict, str

from fastapi import logger
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager

    async def send_user_email(self, user_data: dict, email_type: str):
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification"
        }

        if email_type not in subject_map:
            raise ValueError("Invalid email type")

        html_content = self.template_manager.render_template(email_type, **user_data)
        self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])

    async def send_verification_email(self, user: User):
        if not user.verification_token:
            raise ValueError("User does not have a verification token set.")

        verification_url = f"{settings.server_base_url.rstrip('/')}/verify-email/{user.id}/{user.verification_token}"
    
        logger.info(f"Sending verification email to {user.email} with link: {verification_url}")

        await self.send_user_email(
            {
                "name": user.first_name,
                "verification_url": verification_url,
                "email": user.email
            },
            template_name='email_verification'
        )
