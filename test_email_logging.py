#!/usr/bin/env python3
import logging
import sys
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Create a logger for this script
logger = logging.getLogger("test_email_script")

try:
    logger.info("Testing email notification system with mock mode")
    
    # Initialize services
    template_manager = TemplateManager()
    email_service = EmailService(template_manager)
    
    # Test direct email sending
    logger.info("Sending test email...")
    email_service.smtp_client.send_email(
        'Test Subject',
        '<p>This is a test email from the mock email system</p>',
        'test@example.com'
    )
    logger.info("Test email successfully processed")
    
    print("\nEmail test completed. Check logs above for mock email details.")
    
except Exception as e:
    logger.error(f"Error during email test: {str(e)}")
    print(f"\nEmail test failed: {str(e)}")
    sys.exit(1)
