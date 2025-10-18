"""Basic tests for MailerSlave modules."""

import pytest
from pathlib import Path
import tempfile
import csv


def test_csv_reader():
    """Test CSV reader functionality."""
    from mailerslave.modules import CSVReader

    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=["email", "name"])
        writer.writeheader()
        writer.writerow({"email": "test@example.com", "name": "Test User"})
        temp_csv = f.name

    try:
        reader = CSVReader(temp_csv)
        emails = reader.read_emails()

        assert len(emails) == 1
        assert emails[0]["email"] == "test@example.com"
        assert emails[0]["name"] == "Test User"
        assert reader.get_email_count() == 1
    finally:
        Path(temp_csv).unlink()


def test_csv_reader_missing_file():
    """Test CSV reader with missing file."""
    from mailerslave.modules import CSVReader

    with pytest.raises(FileNotFoundError):
        CSVReader("nonexistent.csv")


def test_template_handler():
    """Test template handler functionality."""
    from mailerslave.modules import TemplateHandler

    # Create a temporary template file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello $name, welcome to $company!")
        temp_template = f.name

    try:
        handler = TemplateHandler(temp_template)
        template = handler.get_template()

        assert "Hello $name" in template

        # Test rendering
        rendered = handler.render_template({"name": "John", "company": "Acme"})
        assert "Hello John, welcome to Acme!" == rendered

        # Test placeholder extraction
        placeholders = handler.extract_placeholders()
        assert "name" in placeholders
        assert "company" in placeholders
    finally:
        Path(temp_template).unlink()


def test_template_handler_missing_file():
    """Test template handler with missing file."""
    from mailerslave.modules import TemplateHandler

    with pytest.raises(FileNotFoundError):
        TemplateHandler("nonexistent.txt")


def test_dry_run_email_sender():
    """Test dry-run email sender."""
    from mailerslave.modules import DryRunEmailSender

    sender = DryRunEmailSender()

    # Test sending (should always succeed in dry-run)
    result = sender.send_email(
        to_email="test@example.com", subject="Test", body="Test body"
    )
    assert result is True

    # Test connection (should always succeed in dry-run)
    assert sender.test_connection() is True


def test_config_defaults():
    """Test configuration defaults."""
    from mailerslave.modules import Config

    config = Config()
    smtp_config = config.get_smtp_config()
    ollama_config = config.get_ollama_config()

    # Test SMTP defaults
    assert smtp_config["smtp_host"] == "smtp.gmail.com"
    assert smtp_config["smtp_port"] == 587
    assert smtp_config["use_tls"] is True

    # Test Ollama defaults
    assert ollama_config["model"] == "llama2"
    assert ollama_config["temperature"] == 0.7
