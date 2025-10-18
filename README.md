# MailerSlave

A modular CLI tool for sending batch emails with LLM-generated personalized content using Ollama API.

## Features

- 📧 **Batch Email Sending**: Send emails to multiple recipients from a CSV file
- 🤖 **LLM-Powered Personalization**: Use Ollama to generate personalized email content
- 📝 **Template System**: Create email templates with variable substitution
- 🔧 **Modular Design**: Well-structured codebase ready for extension to a web service
- 🧪 **Dry Run Mode**: Test your emails without actually sending them
- ⚙️ **Flexible Configuration**: Configure via environment variables or .env files
- 📊 **Progress Tracking**: Real-time logging and summary reports

## Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running (if using LLM features)

### Install from source

```bash
# Clone the repository
git clone https://github.com/Pecneb/MailerSlave.git
cd MailerSlave

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

1. **Create a CSV file** with email addresses and recipient data:

```csv
email,name,company,position
john.doe@example.com,John Doe,Acme Corp,Software Engineer
jane.smith@example.com,Jane Smith,Tech Solutions,Product Manager
```

2. **Create an email template** (see `mailerslave/examples/template.txt`):

```text
Dear $name,

I hope this email finds you well...
```

3. **Configure environment variables** (copy `.env.example` to `.env`):

```bash
cp .env.example .env
# Edit .env with your SMTP credentials
```

4. **Run in dry-run mode** (recommended for testing):

```bash
mailerslave --csv emails.csv --template template.txt --dry-run --subject "Test Email"
```

5. **Send emails** (once configured):

```bash
mailerslave --csv emails.csv --template template.txt --subject "Your Subject"
```

## Usage

### Basic Commands

```bash
# Send emails with LLM-generated content
mailerslave --csv emails.csv --template template.txt --subject "Hello!"

# Dry run (don't actually send emails)
mailerslave --csv emails.csv --template template.txt --dry-run

# Use custom Ollama model
mailerslave --csv emails.csv --template template.txt --model mistral

# Skip LLM generation (use template as-is with variable substitution)
mailerslave --csv emails.csv --template template.txt --no-llm

# Limit the number of emails (useful for testing)
mailerslave --csv emails.csv --template template.txt --limit 5

# Enable verbose logging
mailerslave --csv emails.csv --template template.txt -v
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--csv` | `-c` | Path to CSV file containing email addresses (required) |
| `--template` | `-t` | Path to email template file (required) |
| `--subject` | `-s` | Email subject line |
| `--env-file` | `-e` | Path to .env file for configuration |
| `--model` | `-m` | Ollama model to use (default: llama2) |
| `--ollama-host` | | Ollama API host URL |
| `--temperature` | | Temperature for LLM generation (0.0-1.0, default: 0.7) |
| `--dry-run` | `-d` | Dry run mode - don't actually send emails |
| `--no-llm` | | Skip LLM generation, use template with simple variable substitution |
| `--verbose` | `-v` | Enable verbose logging |
| `--limit` | `-l` | Limit the number of emails to send |

## Configuration

MailerSlave can be configured via environment variables or a `.env` file.

### Environment Variables

#### SMTP Configuration

- `SMTP_HOST`: SMTP server hostname (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_USE_TLS`: Use TLS (default: true)
- `SMTP_FROM_EMAIL`: From email address (defaults to SMTP_USERNAME)

#### Ollama Configuration

- `OLLAMA_MODEL`: Model to use (default: llama2)
- `OLLAMA_HOST`: Ollama API host URL (optional)
- `OLLAMA_TEMPERATURE`: Temperature for generation (default: 0.7)

#### Email Configuration

- `EMAIL_SUBJECT`: Default email subject
- `DRY_RUN`: Enable dry run mode (default: false)

### Example .env file

See `.env.example` for a complete example configuration.

## CSV File Format

The CSV file must contain at least an `email` column. Additional columns can be used as variables in the template.

Example:

```csv
email,name,company,position
john@example.com,John Doe,Acme Corp,Engineer
jane@example.com,Jane Smith,Tech Co,Manager
```

## Template Format

Templates use Python's string Template syntax with `$variable` or `${variable}` placeholders.

Example:

```text
Dear $name,

I hope this email finds you well. I wanted to reach out regarding $company...

Best regards
```

When using LLM generation, the template serves as a base that the LLM will use to generate personalized variations.

## Module Structure

The codebase is organized into modular components for easy extension:

```
mailerslave/
├── __init__.py
├── cli.py                  # CLI interface
├── modules/
│   ├── __init__.py
│   ├── csv_reader.py       # CSV file handling
│   ├── template_handler.py # Template management
│   ├── ollama_generator.py # LLM integration
│   ├── email_sender.py     # SMTP email sending
│   └── config.py           # Configuration management
└── examples/
    ├── emails.csv          # Example CSV file
    └── template.txt        # Example template
```

Each module is self-contained and can be used independently or extended for a web service.

## Future Extensions

This CLI tool is designed with modularity in mind for future extensions:

- 🌐 **Web Interface**: Add a Flask/FastAPI web service
- 📊 **Analytics Dashboard**: Track email open rates and engagement
- 🔄 **Scheduling**: Schedule email campaigns
- 📎 **Attachments**: Support for email attachments
- 🎨 **HTML Templates**: Rich HTML email templates
- 📈 **A/B Testing**: Test different email variations

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest
```

### Code Formatting

```bash
# Format code with black
black mailerslave/

# Lint with ruff
ruff check mailerslave/
```

## Troubleshooting

### Ollama Connection Issues

Make sure Ollama is running:

```bash
ollama serve
```

Check available models:

```bash
ollama list
```

Pull a model if needed:

```bash
ollama pull llama2
```

### Gmail SMTP Issues

If using Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833):

1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `SMTP_PASSWORD`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
