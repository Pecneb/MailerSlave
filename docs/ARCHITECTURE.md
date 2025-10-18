# MailerSlave Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         MailerSlave                              │
│                    Email Automation Tool                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                             │
│                        (cli.py)                                  │
│  - Argument parsing                                              │
│  - User input validation                                         │
│  - Progress reporting                                            │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Core Modules Layer                           │
├──────────────┬────────────┬────────────┬───────────┬────────────┤
│  CSVReader   │  Template  │  Ollama    │   Email   │  Config    │
│              │  Handler   │  Generator │  Sender   │  Manager   │
│              │            │            │           │            │
│ - Parse CSV  │ - Load     │ - Connect  │ - SMTP    │ - Env vars │
│ - Validate   │   template │   to API   │   setup   │ - Defaults │
│ - Extract    │ - Variable │ - Generate │ - Send    │ - Override │
│   data       │   subst.   │   content  │   email   │   handling │
└──────────────┴────────────┴────────────┴───────────┴────────────┘
               │            │            │           │
               ▼            ▼            ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
├──────────────────────────┬──────────────────────────────────────┤
│      Ollama API          │         SMTP Server                   │
│   (LLM Generation)       │      (Email Delivery)                 │
│                          │                                       │
│  - llama2, mistral, etc. │  - Gmail, Outlook, etc.              │
│  - Personalization       │  - TLS/SSL support                   │
│  - Content generation    │  - Authentication                    │
└──────────────────────────┴──────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│  User Input  │
│              │
│ - CSV file   │
│ - Template   │
│ - Config     │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  CSVReader       │
│  reads emails &  │
│  recipient data  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐      ┌──────────────────┐
│ Template Handler │──────┤ Ollama Generator │
│ loads template   │      │ (optional)       │
└──────┬───────────┘      └──────┬───────────┘
       │                         │
       └────────┬────────────────┘
                │
                ▼
       ┌─────────────────┐
       │ Email Content   │
       │ (personalized)  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  Email Sender   │
       │  (SMTP or Dry)  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │   Recipients    │
       │   (or logs)     │
       └─────────────────┘
```

## Module Dependencies

```
cli.py
  ├── modules/csv_reader.py
  ├── modules/template_handler.py
  ├── modules/ollama_generator.py (optional)
  │   └── ollama (external package)
  ├── modules/email_sender.py
  │   └── smtplib (stdlib)
  └── modules/config.py
      └── python-dotenv (external package)
```

## Workflow Modes

### Mode 1: With LLM Generation (Default)
```
CSV + Template → Ollama API → Personalized Emails → SMTP/Dry-run
```

### Mode 2: Without LLM (--no-llm)
```
CSV + Template → Simple Variable Substitution → SMTP/Dry-run
```

### Mode 3: Dry Run (--dry-run)
```
CSV + Template → (Optional LLM) → Log Output (no actual sending)
```

## Configuration Hierarchy

```
1. Default Values (in config.py)
   ↓
2. Environment Variables (.env file)
   ↓
3. Command-line Arguments (highest priority)
```

## Future Web Extension

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface                             │
│                      (Future Addition)                           │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (HTML/React/Vue)                                       │
│     ↓                                                            │
│  REST API (Flask/FastAPI) ← NEW LAYER                           │
│     ↓                                                            │
│  Core Modules ← REUSED (no changes needed)                      │
│     ↓                                                            │
│  External Services ← SAME                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Modularity**: Each module is self-contained and testable
2. **Separation of Concerns**: CLI, business logic, and I/O are separate
3. **Extensibility**: Easy to add new interfaces (web, API, etc.)
4. **Configuration Flexibility**: Multiple ways to configure
5. **Safe Testing**: Dry-run mode for risk-free testing
6. **Error Handling**: Graceful failure with detailed logging
