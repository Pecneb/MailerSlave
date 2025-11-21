"""Email sending service with async support and database logging."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from datetime import datetime

from backend.config import settings
from backend.database import get_database
from backend.models import EmailStatus

logger = logging.getLogger(__name__)


class AsyncEmailSender:
    """Async email sender with database logging."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        from_email: Optional[str] = None,
    ):
        """Initialize the email sender with settings from config or parameters."""
        self.smtp_host = smtp_host or settings.smtp_host
        self.smtp_port = smtp_port or settings.smtp_port
        self.username = username or settings.smtp_username
        self.password = password or settings.smtp_password
        self.use_tls = use_tls if use_tls is not None else settings.smtp_use_tls
        self.from_email = from_email or settings.smtp_from_email or self.username

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        log_to_db: bool = True,
        campaign_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email and optionally log to database.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether the body is HTML
            log_to_db: Whether to log to database
            campaign_id: Associated campaign ID
            contact_id: Associated contact ID
            template_id: Associated template ID

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
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

            # Log to database
            if log_to_db and campaign_id and contact_id:
                await self._log_email(
                    campaign_id=campaign_id,
                    contact_id=contact_id,
                    template_id=template_id,
                    subject=subject,
                    body=body,
                    status=EmailStatus.SENT,
                    error_message=None,
                )

            return True, None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send email to {to_email}: {error_msg}")

            # Log failure to database
            if log_to_db and campaign_id and contact_id:
                await self._log_email(
                    campaign_id=campaign_id,
                    contact_id=contact_id,
                    template_id=template_id,
                    subject=subject,
                    body=body,
                    status=EmailStatus.FAILED,
                    error_message=error_msg,
                )

            return False, error_msg

    async def _log_email(
        self,
        campaign_id: str,
        contact_id: str,
        template_id: Optional[str],
        subject: str,
        body: str,
        status: EmailStatus,
        error_message: Optional[str],
    ):
        """Log email to database."""
        try:
            db = get_database()
            email_log = {
                "campaign_id": campaign_id,
                "contact_id": contact_id,
                "template_id": template_id,
                "subject": subject,
                "body": body,
                "status": status.value,
                "sent_at": datetime.utcnow() if status == EmailStatus.SENT else None,
                "error_message": error_message,
                "created_at": datetime.utcnow(),
            }
            await db.email_logs.insert_one(email_log)
        except Exception as e:
            logger.error(f"Failed to log email to database: {e}")

    def test_connection(self) -> bool:
        """Test SMTP connection and authentication."""
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
    """Email sender that logs emails instead of sending (for testing)."""

    def __init__(self, from_email: str = "test@example.com"):
        """Initialize dry-run email sender."""
        self.from_email = from_email

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        log_to_db: bool = True,
        campaign_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Log email instead of sending."""
        logger.info(f"[DRY RUN] Email to: {to_email}")
        logger.info(f"[DRY RUN] Subject: {subject}")
        logger.info(f"[DRY RUN] Body ({len(body)} chars): {body[:200]}...")

        # Still log to database in dry run mode
        if log_to_db and campaign_id and contact_id:
            try:
                db = get_database()
                email_log = {
                    "campaign_id": campaign_id,
                    "contact_id": contact_id,
                    "template_id": template_id,
                    "subject": subject,
                    "body": body[:500],  # Truncate body in dry run
                    "status": EmailStatus.SENT.value,
                    "sent_at": datetime.utcnow(),
                    "error_message": None,
                    "created_at": datetime.utcnow(),
                }
                await db.email_logs.insert_one(email_log)
            except Exception as e:
                logger.error(f"Failed to log dry run email to database: {e}")

        return True, None

    def test_connection(self) -> bool:
        """Test connection (always succeeds for dry run)."""
        logger.info("[DRY RUN] Connection test - OK")
        return True
