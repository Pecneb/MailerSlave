"""Email sender module for sending emails via SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending emails via SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_email: Optional[str] = None,
    ):
        """
        Initialize the email sender.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS (default: True)
            from_email: From email address (defaults to username if not provided)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_email = from_email or username

    def send_email(
        self, to_email: str, subject: str, body: str, html: bool = False
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether the body is HTML (default: False)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Attach body
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type))

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)

            logger.info("SMTP connection test successful")
            return True

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False


class DryRunEmailSender:
    """Email sender that logs emails instead of actually sending them (for testing)."""

    def __init__(self, from_email: str = "test@example.com"):
        """
        Initialize the dry-run email sender.

        Args:
            from_email: From email address
        """
        self.from_email = from_email

    def send_email(
        self, to_email: str, subject: str, body: str, html: bool = False
    ) -> bool:
        """
        Log an email instead of sending it.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether the body is HTML

        Returns:
            Always returns True
        """
        logger.info(f"[DRY RUN] Email to: {to_email}")
        logger.info(f"[DRY RUN] Subject: {subject}")
        logger.info(f"[DRY RUN] Body ({len(body)} chars): {body[:200]}...")
        return True

    def test_connection(self) -> bool:
        """Test connection (always succeeds for dry run)."""
        logger.info("[DRY RUN] Connection test - OK")
        return True
