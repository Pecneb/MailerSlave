# Contributing to MailerSlave

Thank you for considering contributing to MailerSlave! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/MailerSlave.git
cd MailerSlave
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Install development dependencies:
```bash
pip install pytest black ruff
```

## Development Workflow

### Code Style

We use `black` for code formatting and `ruff` for linting.

```bash
# Format code
black mailerslave/ tests/

# Lint code
ruff check mailerslave/ tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mailerslave tests/

# Run specific test file
pytest tests/test_modules.py -v
```

### Testing Your Changes

Before submitting changes:

1. Run the linter and formatter:
```bash
black mailerslave/ tests/
ruff check mailerslave/ tests/
```

2. Run all tests:
```bash
pytest tests/ -v
```

3. Test the CLI manually:
```bash
mailerslave --csv mailerslave/examples/emails.csv \
            --template mailerslave/examples/template.txt \
            --dry-run --no-llm
```

## Code Organization

```
mailerslave/
├── cli.py                  # CLI entry point
├── modules/
│   ├── csv_reader.py       # CSV handling
│   ├── template_handler.py # Template processing
│   ├── ollama_generator.py # LLM integration
│   ├── email_sender.py     # Email sending
│   └── config.py           # Configuration
└── examples/               # Example files
```

## Adding New Features

### Adding a New Module

1. Create the module in `mailerslave/modules/`
2. Add appropriate docstrings and type hints
3. Export the module in `mailerslave/modules/__init__.py`
4. Add unit tests in `tests/`
5. Update documentation if needed

### Example Module Template

```python
"""Module description."""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MyModule:
    """Class description."""

    def __init__(self, param: str):
        """
        Initialize the module.

        Args:
            param: Description of parameter
        """
        self.param = param

    def do_something(self) -> bool:
        """
        Method description.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Implementation
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
```

## Submitting Changes

1. Create a new branch:
```bash
git checkout -b feature/my-new-feature
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Add my new feature"
```

3. Push to your fork:
```bash
git push origin feature/my-new-feature
```

4. Open a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Test results

## Pull Request Guidelines

- Include tests for new features
- Update documentation as needed
- Follow existing code style
- Keep PRs focused on a single feature/fix
- Write clear commit messages

## Reporting Issues

When reporting issues, please include:

- Python version
- MailerSlave version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Environment details (OS, etc.)

## Feature Requests

We welcome feature requests! Please:

- Check existing issues first
- Describe the use case
- Explain why it would be useful
- Consider if it fits the project scope

## Questions?

Feel free to open an issue for questions or discussions.

Thank you for contributing!
