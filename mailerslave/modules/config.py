"""Configuration management module."""

import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Manages configuration from environment variables and .env files."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Optional path to .env file
        """
        # Load .env file if specified
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            # Try to load from default .env in current directory
            default_env = Path(".env")
            if default_env.exists():
                load_dotenv(default_env)
                logger.info("Loaded configuration from .env")

    @staticmethod
    def get_smtp_config() -> Dict[str, any]:
        """
        Get SMTP configuration from environment variables.

        Returns:
            Dictionary containing SMTP configuration
        """
        return {
            "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            "from_email": os.getenv("SMTP_FROM_EMAIL"),
        }

    @staticmethod
    def get_ollama_config() -> Dict[str, any]:
        """
        Get Ollama configuration from environment variables.

        Returns:
            Dictionary containing Ollama configuration
        """
        return {
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "host": os.getenv("OLLAMA_HOST"),
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
        }

    @staticmethod
    def get_email_config() -> Dict[str, str]:
        """
        Get email-specific configuration.

        Returns:
            Dictionary containing email configuration
        """
        return {
            "subject": os.getenv("EMAIL_SUBJECT", ""),
            "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
        }
