#!/usr/bin/env python3
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test SMTP configuration with simple approach
def test_direct_smtp():
    # Mailtrap credentials
    smtp_server = "sandbox.smtp.mailtrap.io"
    port = 2525
    sender_email = "956e497195a1db"  # Mailtrap username
    password = "bbde0"               # Password to test
    receiver_email = "test@example.com"
    
    logger.info(f"Testing connection to {smtp_server}:{port} with {sender_email}")
    
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Create message
        message = MIMEMultipart()
        message["Subject"] = "Direct SMTP Test"
        message["From"] = sender_email
        message["To"] = receiver_email
        
        # Add body
        body = "This is a test email sent directly from Python."
        message.attach(MIMEText(body, "plain"))
        
        # Try to send email
        with smtplib.SMTP(smtp_server, port) as server:
            server.set_debuglevel(1)  # Show all SMTP commands
            server.ehlo()  # Identify to SMTP server
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Re-identify on TLS connection
            
            logger.info("Attempting to log in...")
            server.login(sender_email, password)
            logger.info("Login successful!")
            
            logger.info(f"Sending email to {receiver_email}")
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger.info("Email sent successfully!")
            
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    print("======= Testing Direct SMTP Connection =======")
    success = test_direct_smtp()
    print(f"Email test {'successful' if success else 'failed'}")
    
    if not success:
        print("\nSuggested fixes:")
        print("1. Verify Mailtrap credentials (username and password)")
        print("2. Try a different SMTP port (25, 465, 587, or 2525)")
        print("3. If behind a firewall, make sure outbound SMTP is allowed")
        print("4. For testing, set SEND_REAL_MAIL=false in environment variables")
