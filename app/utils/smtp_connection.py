# smtp_client.py
from builtins import Exception, int, str
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings.config import settings
import logging
import socket
import time
import base64
from typing import Optional

class SMTPClient:
    def __init__(self, server: str, port: int, username: str, password: str):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)

    def _connect_with_retry(self, max_retries=3, retry_delay=2) -> Optional[smtplib.SMTP]:
        """Attempt to connect to the SMTP server with retries"""
        self.logger.info(f"Connecting to SMTP server {self.server}:{self.port}")
        
        for attempt in range(max_retries):
            try:
                # Add timeout to avoid hanging
                smtp = smtplib.SMTP(self.server, self.port, timeout=10)
                smtp.set_debuglevel(1)  # Enable debug output for troubleshooting
                self.logger.info("SMTP connection established")
                
                # Get server capabilities
                smtp.ehlo_or_helo_if_needed()
                if smtp.has_extn('STARTTLS'):
                    self.logger.info("Starting TLS session")
                    smtp.starttls()
                    smtp.ehlo()  # Re-identify after TLS
                else:
                    self.logger.warning("STARTTLS not supported by server")
                
                return smtp
            except (socket.error, smtplib.SMTPException) as e:
                self.logger.error(f"SMTP connection attempt {attempt+1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error("All connection attempts failed")
                    raise
        return None

    def send_email(self, subject: str, html_content: str, recipient: str):
        try:
            # Prepare email message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.username
            message['To'] = recipient
            message.attach(MIMEText(html_content, 'html'))
            
            # Check if we should send real emails or just log them
            send_real_mail = False
            if hasattr(settings, 'send_real_mail'):
                # Handle string value 'true'/'false' or boolean True/False
                if isinstance(settings.send_real_mail, str):
                    send_real_mail = settings.send_real_mail.lower() == 'true'
                else:
                    send_real_mail = bool(settings.send_real_mail)
            
            # If SEND_REAL_MAIL is false, just log the email content and return
            if not send_real_mail:
                self.logger.info(f"\n==========MOCK EMAIL==========")
                self.logger.info(f"TO: {recipient}")
                self.logger.info(f"FROM: {self.username}")
                self.logger.info(f"SUBJECT: {subject}")
                self.logger.info(f"CONTENT:\n{html_content}")
                self.logger.info(f"============================\n")
                return
                
            # Only attempt connection if we're sending real emails
            # Connect to SMTP server with retry logic
            smtp = self._connect_with_retry()
            if not smtp:
                raise Exception("Failed to connect to SMTP server after retries")
                
            # Authenticate with explicit mechanism
            self.logger.info(f"Authenticating as {self.username}")
            try:
                # Try PLAIN authentication first
                smtp.login(self.username, self.password)
            except smtplib.SMTPException as auth_error:
                self.logger.error(f"Standard login failed: {str(auth_error)}")
                # Try manually crafting AUTH LOGIN as a fallback
                try:
                    self.logger.info("Attempting alternative authentication method...")
                    smtp.docmd("AUTH LOGIN")
                    smtp.docmd(base64.b64encode(self.username.encode()).decode())
                    smtp.docmd(base64.b64encode(self.password.encode()).decode())
                except Exception as e:
                    self.logger.error(f"Alternative authentication failed: {str(e)}")
                    raise
                    
            # Send the email
            self.logger.info(f"Sending email to {recipient}")
            smtp.sendmail(self.username, recipient, message.as_string())
            self.logger.info(f"Email successfully sent to {recipient}")
            
            # Close connection
            try:
                smtp.quit()
            except Exception as e:
                self.logger.warning(f"Error during SMTP quit: {str(e)}")
                
        except Exception as e:
            # For mock email mode, don't propagate SMTP connection errors
            send_real_mail = False
            if hasattr(settings, 'send_real_mail'):
                # Handle string value 'true'/'false' or boolean True/False
                if isinstance(settings.send_real_mail, str):
                    send_real_mail = settings.send_real_mail.lower() == 'true'
                else:
                    send_real_mail = bool(settings.send_real_mail)
                
            if not send_real_mail:
                self.logger.warning(f"Mock email mode: Ignoring SMTP error: {str(e)}")
                return
                
            # For real email mode, log errors and propagate them
            self.logger.error(f"Failed to send email: {str(e)}")
            self.logger.error(f"SMTP details: server={self.server}, port={self.port}, username={self.username}")
            raise
