"""Modules initialization."""

from .csv_reader import CSVReader
from .template_handler import TemplateHandler
from .ollama_generator import OllamaGenerator
from .email_sender import EmailSender, DryRunEmailSender
from .config import Config

__all__ = [
    "CSVReader",
    "TemplateHandler",
    "OllamaGenerator",
    "EmailSender",
    "DryRunEmailSender",
    "Config",
]
