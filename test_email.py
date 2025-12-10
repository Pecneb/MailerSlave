#!/usr/bin/env python3
"""
Quick email sender test script
Tests SMTP connection and sends a test email without needing the full app.

Usage:
    python test_email.py

Configure via .env file or edit the variables below.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============= CONFIGURATION =============
# Edit these or set them in your .env file

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-app-password')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)

# Test email recipient (change this to your email)
TO_EMAIL = os.getenv('TEST_EMAIL', SMTP_USERNAME)

# =========================================


def test_connection():
    """Test SMTP connection and authentication."""
    print("=" * 60)
    print("SMTP CONNECTION TEST")
    print("=" * 60)
    print(f"Host:     {SMTP_HOST}")
    print(f"Port:     {SMTP_PORT}")
    print(f"Username: {SMTP_USERNAME}")
    print(f"Password: {'*' * len(SMTP_PASSWORD)}")
    print(f"Use TLS:  {SMTP_USE_TLS}")
    print(f"From:     {FROM_EMAIL}")
    print("=" * 60)
    
    try:
        print("\n[1/4] Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        print("✅ Connected successfully!")
        
        print("\n[2/4] Starting TLS encryption...")
        if SMTP_USE_TLS:
            server.starttls()
            print("✅ TLS started successfully!")
        else:
            print("⚠️  TLS disabled (not recommended)")
        
        print("\n[3/4] Authenticating...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ Authentication successful!")
        
        print("\n[4/4] Closing connection...")
        server.quit()
        print("✅ Connection closed\n")
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED - SMTP is configured correctly!")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("  1. For Gmail, you MUST use an App Password, not your regular password")
        print("  2. Enable 2-Factor Authentication first")
        print("  3. Generate App Password: https://myaccount.google.com/apppasswords")
        print("  4. Use the 16-character App Password (remove spaces)")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False


def send_test_email():
    """Send a test email."""
    print("\n" + "=" * 60)
    print("SENDING TEST EMAIL")
    print("=" * 60)
    print(f"To: {TO_EMAIL}")
    print("=" * 60)
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🧪 MailerSlave Test Email"
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        
        # Email body
        text = """
Hello!

This is a test email from MailerSlave.

If you're receiving this, your SMTP configuration is working correctly! 🎉

Configuration used:
- Host: {}
- Port: {}
- From: {}

Best regards,
MailerSlave Test Script
        """.format(SMTP_HOST, SMTP_PORT, FROM_EMAIL)
        
        html = """
<html>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>🧪 MailerSlave Test Email</h2>
    <p>Hello!</p>
    <p>This is a test email from <strong>MailerSlave</strong>.</p>
    <p>If you're receiving this, your SMTP configuration is working correctly! 🎉</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
      <strong>Configuration used:</strong><br>
      Host: {}<br>
      Port: {}<br>
      From: {}
    </p>
    <p style="color: #666; font-size: 12px;">
      Best regards,<br>
      MailerSlave Test Script
    </p>
  </body>
</html>
        """.format(SMTP_HOST, SMTP_PORT, FROM_EMAIL)
        
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))
        
        # Connect and send
        print("\nConnecting to SMTP server...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        
        if SMTP_USE_TLS:
            server.starttls()
        
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your inbox at: {TO_EMAIL}")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED TO SEND EMAIL: {e}")
        print("=" * 60)
        return False


def main():
    """Main test function."""
    print("\n🚀 MailerSlave SMTP Test Script")
    print("Testing email configuration from .env file\n")
    
    # Test connection first
    if test_connection():
        # If connection works, offer to send test email
        response = input("\n📧 Send a test email? (y/n): ").lower()
        if response == 'y':
            send_test_email()
    else:
        print("\n⚠️  Fix the connection issues above before sending emails.")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
