#!/usr/bin/env python3
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test SMTP configuration with Mailtrap
def test_smtp_connection(server, port, username, password, recipient="test@example.com"):
    print(f"Testing SMTP connection to {server}:{port} with username {username}")
    
    try:
        # Create connection with debug output
        smtp = smtplib.SMTP(server, port)
        smtp.set_debuglevel(1)
        
        # Identify to ESMTP server
        smtp.ehlo()
        
        # Use TLS for encryption
        if smtp.has_extn('STARTTLS'):
            print("Starting TLS...")
            smtp.starttls()
            smtp.ehlo()  # Re-identify after TLS
            
        print(f"Authenticating as {username}...")
        smtp.login(username, password)
        print("Authentication successful!")

        # Prepare and send test message
        message = MIMEMultipart()
        message['Subject'] = "SMTP Test Email"
        message['From'] = username
        message['To'] = recipient
        
        body = MIMEText("<h1>This is a test email</h1><p>Successfully sent from the User Management System</p>", 'html')
        message.attach(body)
        
        print(f"Sending test email to {recipient}...")
        smtp.sendmail(username, recipient, message.as_string())
        print("Email sent successfully!")
        
        # Close connection
        smtp.quit()
        return True
        
    except Exception as e:
        print(f"SMTP Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Get password from command line if provided
    password = sys.argv[1] if len(sys.argv) > 1 else "bbde0"
    
    # Mailtrap credentials
    server = "sandbox.smtp.mailtrap.io"
    port = 2525
    username = "956e497195a1db"
    
    success = test_smtp_connection(server, port, username, password)
    sys.exit(0 if success else 1)
