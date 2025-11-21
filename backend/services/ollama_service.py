"""Ollama LLM service for generating personalized email content."""

import ollama
from typing import Dict, Optional
import logging

from backend.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Generates personalized email content using Ollama LLM API."""

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize Ollama service with settings from config or parameters."""
        self.model = model or settings.ollama_model
        self.temperature = temperature if temperature is not None else settings.ollama_temperature
        self.host = host or settings.ollama_host
        self.client = ollama.Client(host=self.host) if self.host else ollama.Client()

    async def generate_email(
        self,
        template: str,
        recipient_data: Dict[str, str],
        system_prompt: Optional[str] = None,
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

        # Create prompt combining template and recipient data
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
        """Format recipient data for the prompt."""
        return "\n".join([f"- {key}: {value}" for key, value in data.items()])

    def test_connection(self) -> bool:
        """Test the connection to Ollama API."""
        try:
            models = self.client.list()
            logger.info(f"Ollama connection test successful. Available models: {len(models.get('models', []))}")
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False

    def check_model_available(self) -> bool:
        """Check if the configured model is available."""
        try:
            models = self.client.list()
            model_names = [m["name"] for m in models.get("models", [])]
            available = self.model in model_names
            if not available:
                logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
            return available
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
