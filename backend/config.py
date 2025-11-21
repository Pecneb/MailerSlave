"""Configuration management for FastAPI backend."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "mailerslave"
    
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from_email: Optional[str] = None
    
    # Ollama
    ollama_model: str = "llama2"
    ollama_host: Optional[str] = None
    ollama_temperature: float = 0.7
    
    # Application
    app_name: str = "MailerSlave"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
