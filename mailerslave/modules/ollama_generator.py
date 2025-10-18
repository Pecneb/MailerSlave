"""Ollama LLM integration module for generating personalized email content."""

import ollama
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaGenerator:
    """Generates personalized email content using Ollama LLM API."""

    def __init__(
        self, model: str = "llama2", host: Optional[str] = None, temperature: float = 0.7
    ):
        """
        Initialize the Ollama generator.

        Args:
            model: Name of the Ollama model to use (default: llama2)
            host: Optional Ollama host URL
            temperature: Temperature for generation (0.0-1.0, default: 0.7)
        """
        self.model = model
        self.temperature = temperature
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def generate_email(
        self, template: str, recipient_data: Dict[str, str], system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a personalized email using the LLM.

        Args:
            template: Base email template
            recipient_data: Dictionary containing recipient-specific data
            system_prompt: Optional system prompt to guide the LLM

        Returns:
            Generated email content
        """
        if system_prompt is None:
            system_prompt = (
                "You are an expert email writer. Generate a personalized, professional email "
                "based on the template and recipient data provided. Maintain the tone and "
                "structure of the template while personalizing the content. "
                "Return only the email content without any additional commentary."
            )

        # Create a prompt combining template and recipient data
        user_prompt = f"""Template:
{template}

Recipient Data:
{self._format_recipient_data(recipient_data)}

Please generate a personalized email based on the template above, incorporating the recipient data naturally."""

        try:
            logger.info(f"Generating email for recipient: {recipient_data.get('email', 'unknown')}")

            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": self.temperature},
            )

            generated_content = response["message"]["content"]
            logger.debug(f"Generated email length: {len(generated_content)} characters")

            return generated_content

        except Exception as e:
            logger.error(f"Error generating email with Ollama: {e}")
            raise RuntimeError(f"Failed to generate email: {e}")

    def _format_recipient_data(self, data: Dict[str, str]) -> str:
        """
        Format recipient data for the prompt.

        Args:
            data: Recipient data dictionary

        Returns:
            Formatted string representation
        """
        return "\n".join([f"- {key}: {value}" for key, value in data.items()])

    def test_connection(self) -> bool:
        """
        Test the connection to Ollama API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to list available models
            models = self.client.list()
            logger.info(f"Connected to Ollama. Available models: {len(models.get('models', []))}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def check_model_available(self) -> bool:
        """
        Check if the specified model is available.

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = self.client.list()
            model_names = [m["name"] for m in models.get("models", [])]
            available = any(self.model in name for name in model_names)

            if not available:
                logger.warning(
                    f"Model '{self.model}' not found. Available models: {model_names}"
                )

            return available
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
