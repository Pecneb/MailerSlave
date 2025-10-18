# MailerSlave Usage Guide

This guide provides detailed instructions for using MailerSlave.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Email Templates](#email-templates)
4. [CSV File Format](#csv-file-format)
5. [LLM Integration](#llm-integration)
6. [SMTP Setup](#smtp-setup)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Dry Run (No Email Sending)

This is the safest way to test MailerSlave:

```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --subject "Test Email" \
  --dry-run \
  --no-llm
```

This will:
- Read emails from `emails.csv`
- Use the template from `template.txt`
- NOT send actual emails (dry-run mode)
- NOT use LLM (simple variable substitution only)

### With LLM Generation (Dry Run)

```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --subject "Test Email" \
  --dry-run \
  --model llama2
```

This requires Ollama to be running.

### Actual Email Sending

Once you've tested with dry-run:

```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --subject "Your Subject" \
  --limit 5
```

The `--limit 5` flag ensures you only send to the first 5 recipients (recommended for initial tests).

## Configuration

### Environment Variables

Create a `.env` file in your project directory:

```env
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com

# Ollama Settings
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.7

# Email Settings
EMAIL_SUBJECT=Default Subject
DRY_RUN=false
```

### Command-Line Overrides

Command-line arguments override environment variables:

```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --model mistral \           # Override OLLAMA_MODEL
  --temperature 0.9 \         # Override OLLAMA_TEMPERATURE
  --subject "Custom" \        # Override EMAIL_SUBJECT
  --dry-run                   # Override DRY_RUN
```

## Email Templates

Templates use Python's Template syntax with `$variable` placeholders.

### Basic Template

```text
Dear $name,

I hope this email finds you well.

Best regards
```

### Template with Multiple Variables

```text
Dear $name,

Thank you for your interest in $product.

As a $position at $company, you might be interested in our special offer.

Best regards,
The Team
```

### Important Notes

- Variable names must match CSV column headers
- Variables are case-sensitive
- Use `${variable}` for variables adjacent to text: `${name}s` → "Johns"
- Missing variables are left as-is when using `--no-llm`

## CSV File Format

### Basic Format

```csv
email,name
john@example.com,John Doe
jane@example.com,Jane Smith
```

### Extended Format

```csv
email,name,company,position,product
john@example.com,John Doe,Acme Corp,Engineer,Premium Plan
jane@example.com,Jane Smith,Tech Co,Manager,Enterprise Suite
```

### Requirements

- **Must** have an `email` column
- Column headers become template variables
- CSV should be UTF-8 encoded
- Empty email rows are skipped

### Example CSV Creation

**Excel/Google Sheets:**
1. Create your spreadsheet with email column
2. File → Export → CSV

**Python:**
```python
import csv

data = [
    {"email": "user@example.com", "name": "User Name"},
    # more rows...
]

with open("emails.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["email", "name"])
    writer.writeheader()
    writer.writerows(data)
```

## LLM Integration

### Setting Up Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai)

2. Start Ollama:
```bash
ollama serve
```

3. Pull a model:
```bash
ollama pull llama2
```

4. Test connection:
```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --dry-run \
  --limit 1
```

### Available Models

Popular models you can use:
- `llama2` - Default, good balance
- `mistral` - Fast and efficient
- `llama3` - Latest version
- `codellama` - For technical content
- `phi` - Smaller, faster model

Pull models with:
```bash
ollama pull <model-name>
```

### LLM vs No-LLM Mode

**With LLM (`default`):**
- Generates unique, personalized variations
- Maintains template's tone and structure
- Requires Ollama running
- Slower but more natural

**Without LLM (`--no-llm`):**
- Simple variable substitution
- Faster processing
- No Ollama needed
- All emails follow exact template structure

## SMTP Setup

### Gmail Setup

1. Enable 2-Factor Authentication on your Google account

2. Generate App Password:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Select "2-Step Verification"
   - Scroll to "App passwords"
   - Generate password for "Mail"

3. Use in `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

### Other SMTP Providers

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP:**
```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

## Common Use Cases

### 1. Newsletter Campaign

```bash
# Test with first 5 recipients
mailerslave \
  --csv subscribers.csv \
  --template newsletter.txt \
  --subject "Monthly Newsletter - October 2025" \
  --limit 5 \
  --dry-run

# Send to all after verification
mailerslave \
  --csv subscribers.csv \
  --template newsletter.txt \
  --subject "Monthly Newsletter - October 2025"
```

### 2. Personalized Outreach

```bash
# Use LLM for personalization
mailerslave \
  --csv prospects.csv \
  --template outreach.txt \
  --subject "Partnership Opportunity" \
  --model mistral \
  --temperature 0.8
```

### 3. Event Invitations

```bash
# Simple template substitution (faster)
mailerslave \
  --csv attendees.csv \
  --template invitation.txt \
  --subject "You're Invited!" \
  --no-llm
```

### 4. Testing/Development

```bash
# Verbose logging for debugging
mailerslave \
  --csv test.csv \
  --template test.txt \
  --dry-run \
  --verbose \
  --limit 1
```

## Troubleshooting

### Ollama Connection Failed

**Error:** "Failed to connect to Ollama"

**Solutions:**
1. Check Ollama is running: `ollama serve`
2. Verify model is installed: `ollama list`
3. Pull model if needed: `ollama pull llama2`
4. Use `--no-llm` flag to skip LLM generation

### SMTP Authentication Failed

**Error:** "SMTP connection test failed"

**Solutions:**
1. Check credentials in `.env`
2. For Gmail, use App Password (not account password)
3. Verify SMTP host and port
4. Test with dry-run first: `--dry-run`

### CSV File Not Found

**Error:** "CSV file not found"

**Solutions:**
1. Check file path is correct
2. Use absolute path if needed
3. Verify file exists: `ls -la emails.csv`

### Template Variables Not Substituting

**Issue:** Variables like `$name` appear in output

**Solutions:**
1. Check CSV has matching column header
2. Variable names are case-sensitive
3. Use `${name}` syntax if variable is adjacent to text
4. When using LLM, it should handle missing variables gracefully

### Rate Limiting

If sending many emails:

1. Use `--limit` to control batch size
2. Add delays between batches (run multiple times)
3. Check your SMTP provider's rate limits
4. Consider using a transactional email service for large volumes

### Verbose Logging

For debugging, enable verbose mode:

```bash
mailerslave \
  --csv emails.csv \
  --template template.txt \
  --verbose \
  --dry-run
```

This shows detailed logs of:
- Configuration loading
- Module initialization
- Email processing
- SMTP/Ollama connections

## Best Practices

1. **Always test with dry-run first**
   ```bash
   --dry-run --limit 5
   ```

2. **Start with small batches**
   ```bash
   --limit 10
   ```

3. **Use verbose logging during development**
   ```bash
   --verbose
   ```

4. **Keep templates professional**
   - Test LLM output with dry-run
   - Adjust temperature if needed (0.5-1.0)

5. **Backup your CSV files**
   - Keep original copies
   - Version control templates

6. **Monitor email delivery**
   - Check spam folders
   - Review bounce messages
   - Respect unsubscribe requests

## Getting Help

- GitHub Issues: [Report bugs or request features](https://github.com/Pecneb/MailerSlave/issues)
- Documentation: See main [README.md](README.md)
- Contributing: See [CONTRIBUTING.md](CONTRIBUTING.md)
