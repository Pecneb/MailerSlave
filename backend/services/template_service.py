"""Template rendering service."""

from string import Template
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Handles template rendering and variable substitution."""

    @staticmethod
    def render_template(template_content: str, variables: Dict[str, str]) -> str:
        """
        Render a template with provided variables.

        Args:
            template_content: Template string
            variables: Dictionary of variables to substitute

        Returns:
            Rendered template string
        """
        try:
            template = Template(template_content)
            return template.safe_substitute(variables)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            raise ValueError(f"Error rendering template: {e}")

    @staticmethod
    def extract_placeholders(template_content: str) -> List[str]:
        """
        Extract placeholder variables from a template.

        Args:
            template_content: Template string

        Returns:
            List of placeholder variable names
        """
        pattern = r"\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?"
        placeholders = re.findall(pattern, template_content)
        return list(set(placeholders))
