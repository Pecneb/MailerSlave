"""CLI interface for MailerSlave."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from mailerslave.modules import (
    CSVReader,
    TemplateHandler,
    OllamaGenerator,
    EmailSender,
    DryRunEmailSender,
    Config,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up and return the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="MailerSlave - Send batch emails with LLM-generated content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send emails using default configuration from .env
  mailerslave --csv emails.csv --template template.txt --subject "Hello!"

  # Dry run (don't actually send emails)
  mailerslave --csv emails.csv --template template.txt --dry-run

  # Use custom Ollama model
  mailerslave --csv emails.csv --template template.txt --model mistral

  # Use custom environment file
  mailerslave --csv emails.csv --template template.txt --env-file config.env

  # Enable verbose logging
  mailerslave --csv emails.csv --template template.txt -v

  # Send without LLM generation (use template as-is with variable substitution)
  mailerslave --csv emails.csv --template template.txt --no-llm
        """,
    )

    # Required arguments
    parser.add_argument(
        "--csv", "-c", required=True, help="Path to CSV file containing email addresses"
    )

    parser.add_argument(
        "--template", "-t", required=True, help="Path to email template file"
    )

    # Optional arguments
    parser.add_argument("--subject", "-s", help="Email subject line")

    parser.add_argument(
        "--env-file", "-e", help="Path to .env file for configuration"
    )

    parser.add_argument(
        "--model", "-m", help="Ollama model to use (default: llama2)"
    )

    parser.add_argument(
        "--ollama-host", help="Ollama API host URL"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        help="Temperature for LLM generation (0.0-1.0, default: 0.7)",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Dry run mode - don't actually send emails",
    )

    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM generation, use template with simple variable substitution only",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit the number of emails to send (useful for testing)",
    )

    return parser


def validate_inputs(csv_path: str, template_path: str) -> bool:
    """
    Validate input files exist.

    Args:
        csv_path: Path to CSV file
        template_path: Path to template file

    Returns:
        True if all inputs are valid, False otherwise
    """
    csv_file = Path(csv_path)
    template_file = Path(template_path)

    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return False

    if not template_file.exists():
        logger.error(f"Template file not found: {template_path}")
        return False

    return True


def send_emails(
    csv_reader: CSVReader,
    template_handler: TemplateHandler,
    email_sender: EmailSender,
    ollama_generator: Optional[OllamaGenerator],
    subject: str,
    limit: Optional[int] = None,
    use_llm: bool = True,
) -> tuple[int, int]:
    """
    Send emails to all recipients.

    Args:
        csv_reader: CSV reader instance
        template_handler: Template handler instance
        email_sender: Email sender instance
        ollama_generator: Ollama generator instance (optional)
        subject: Email subject
        limit: Maximum number of emails to send
        use_llm: Whether to use LLM for generation

    Returns:
        Tuple of (successful_count, failed_count)
    """
    recipients = csv_reader.read_emails()
    total = len(recipients)

    if limit:
        recipients = recipients[:limit]
        logger.info(f"Limiting to {limit} emails out of {total} total")

    logger.info(f"Sending emails to {len(recipients)} recipient(s)")

    successful = 0
    failed = 0

    for i, recipient_data in enumerate(recipients, 1):
        email_address = recipient_data.get("email")
        logger.info(f"[{i}/{len(recipients)}] Processing: {email_address}")

        try:
            # Generate or render email content
            if use_llm and ollama_generator:
                template = template_handler.get_template()
                email_body = ollama_generator.generate_email(template, recipient_data)
            else:
                email_body = template_handler.render_template(recipient_data)

            # Send email
            success = email_sender.send_email(
                to_email=email_address, subject=subject, body=email_body
            )

            if success:
                successful += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"Error processing {email_address}: {e}")
            failed += 1

    return successful, failed


def main():
    """Main CLI entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Validate inputs
    if not validate_inputs(args.csv, args.template):
        sys.exit(1)

    # Load configuration
    config = Config(args.env_file)
    smtp_config = config.get_smtp_config()
    ollama_config = config.get_ollama_config()
    email_config = config.get_email_config()

    # Override config with command-line arguments
    if args.model:
        ollama_config["model"] = args.model
    if args.ollama_host:
        ollama_config["host"] = args.ollama_host
    if args.temperature is not None:
        ollama_config["temperature"] = args.temperature
    if args.dry_run:
        email_config["dry_run"] = True

    # Determine subject
    subject = args.subject or email_config.get("subject") or "Email from MailerSlave"

    # Initialize modules
    try:
        logger.info("Initializing modules...")

        csv_reader = CSVReader(args.csv)
        template_handler = TemplateHandler(args.template)

        # Initialize email sender
        if email_config["dry_run"]:
            logger.info("Running in DRY RUN mode - emails will not be sent")
            email_sender = DryRunEmailSender()
        else:
            if not smtp_config["username"] or not smtp_config["password"]:
                logger.error(
                    "SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD "
                    "environment variables or use --dry-run for testing."
                )
                sys.exit(1)

            email_sender = EmailSender(**smtp_config)

            # Test SMTP connection
            logger.info("Testing SMTP connection...")
            if not email_sender.test_connection():
                logger.error("SMTP connection test failed. Please check your configuration.")
                sys.exit(1)

        # Initialize Ollama generator (if not using --no-llm)
        ollama_generator = None
        if not args.no_llm:
            logger.info(f"Initializing Ollama with model: {ollama_config['model']}")
            ollama_generator = OllamaGenerator(**ollama_config)

            # Test Ollama connection
            logger.info("Testing Ollama connection...")
            if not ollama_generator.test_connection():
                logger.error(
                    "Failed to connect to Ollama. Make sure Ollama is running. "
                    "Use --no-llm to skip LLM generation."
                )
                sys.exit(1)

            # Check if model is available
            if not ollama_generator.check_model_available():
                logger.warning(
                    f"Model '{ollama_config['model']}' may not be available. "
                    "Email generation might fail."
                )
        else:
            logger.info("LLM generation disabled - using simple template substitution")

        # Get email count
        email_count = csv_reader.get_email_count()
        logger.info(f"Found {email_count} email(s) in CSV file")

        # Send emails
        successful, failed = send_emails(
            csv_reader=csv_reader,
            template_handler=template_handler,
            email_sender=email_sender,
            ollama_generator=ollama_generator,
            subject=subject,
            limit=args.limit,
            use_llm=not args.no_llm,
        )

        # Summary
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total emails processed: {successful + failed}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info("=" * 60)

        if failed > 0:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
