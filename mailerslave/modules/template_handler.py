"""Template handler module for managing email templates."""

from pathlib import Path
from string import Template
from typing import Dict


class TemplateHandler:
    """Handles email template loading and variable substitution."""

    def __init__(self, template_path: str):
        """
        Initialize the template handler.

        Args:
            template_path: Path to the email template file
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(self.template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()

    def get_template(self) -> str:
        """
        Get the raw template content.

        Returns:
            Template content as string
        """
        return self.template_content

    def render_template(self, variables: Dict[str, str]) -> str:
        """
        Render the template with provided variables using simple substitution.

        Args:
            variables: Dictionary of variables to substitute

        Returns:
            Rendered template string
        """
        template = Template(self.template_content)
        try:
            return template.safe_substitute(variables)
        except Exception as e:
            raise ValueError(f"Error rendering template: {e}")

    def extract_placeholders(self) -> set:
        """
        Extract placeholder variables from the template.

        Returns:
            Set of placeholder variable names
        """
        template = Template(self.template_content)
        # This is a simple extraction - Template doesn't provide this directly
        import re

        pattern = r"\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?"
        placeholders = set(re.findall(pattern, self.template_content))
        return placeholders
