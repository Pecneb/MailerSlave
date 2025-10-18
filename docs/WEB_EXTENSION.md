# Web Service Extension Guide

This guide explains how to extend MailerSlave into a web service with a simple GUI.

## Architecture Overview

The current CLI implementation is designed with modularity in mind, making it easy to add a web interface:

```
Current (CLI):
User → CLI → Modules → SMTP/Ollama

Future (Web):
User → Web UI → API → Modules → SMTP/Ollama
```

## Recommended Stack

### Backend Framework Options

**Flask (Recommended for simplicity):**
```python
from flask import Flask, request, jsonify
from mailerslave.modules import CSVReader, TemplateHandler, OllamaGenerator

app = Flask(__name__)

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    # Use existing modules
    csv_reader = CSVReader(csv_path)
    # ... rest of logic
```

**FastAPI (Recommended for async/performance):**
```python
from fastapi import FastAPI, UploadFile
from mailerslave.modules import CSVReader, TemplateHandler

app = FastAPI()

@app.post("/api/send-emails")
async def send_emails(csv_file: UploadFile, template: UploadFile):
    # Use existing modules
    # ...
```

### Frontend Options

1. **Simple HTML/JavaScript** - No framework needed
2. **React** - For complex interactions
3. **Vue.js** - Lightweight and flexible
4. **Streamlit** - Fastest to implement

## Implementation Steps

### Phase 1: API Layer

Create `mailerslave/api.py`:

```python
"""REST API for MailerSlave."""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

from mailerslave.modules import (
    CSVReader,
    TemplateHandler,
    OllamaGenerator,
    EmailSender,
    DryRunEmailSender,
    Config
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Send batch emails endpoint."""
    
    # Get uploaded files
    csv_file = request.files.get('csv')
    template_file = request.files.get('template')
    
    # Get parameters
    subject = request.form.get('subject')
    dry_run = request.form.get('dry_run', 'false').lower() == 'true'
    use_llm = request.form.get('use_llm', 'true').lower() == 'true'
    model = request.form.get('model', 'llama2')
    
    # Save files temporarily
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, secure_filename(csv_file.filename))
        template_path = os.path.join(tmpdir, secure_filename(template_file.filename))
        
        csv_file.save(csv_path)
        template_file.save(template_path)
        
        # Use existing modules
        try:
            csv_reader = CSVReader(csv_path)
            template_handler = TemplateHandler(template_path)
            
            # Process emails...
            
            return jsonify({
                'success': True,
                'message': 'Emails sent successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@app.route('/api/preview', methods=['POST'])
def preview_email():
    """Preview generated email endpoint."""
    # Similar to send_emails but only generate preview
    pass

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
```

### Phase 2: Simple Web UI

Create `mailerslave/static/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>MailerSlave</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <h1>📧 MailerSlave</h1>
    <p>Send batch emails with LLM-generated content</p>
    
    <form id="emailForm">
        <div class="form-group">
            <label for="csvFile">CSV File:</label>
            <input type="file" id="csvFile" accept=".csv" required>
        </div>
        
        <div class="form-group">
            <label for="templateFile">Template File:</label>
            <input type="file" id="templateFile" accept=".txt" required>
        </div>
        
        <div class="form-group">
            <label for="subject">Email Subject:</label>
            <input type="text" id="subject" required>
        </div>
        
        <div class="form-group">
            <label for="model">LLM Model:</label>
            <select id="model">
                <option value="llama2">Llama 2</option>
                <option value="mistral">Mistral</option>
                <option value="phi">Phi</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>
                <input type="checkbox" id="dryRun" checked>
                Dry Run (don't send actual emails)
            </label>
        </div>
        
        <div class="form-group">
            <label>
                <input type="checkbox" id="useLLM" checked>
                Use LLM for personalization
            </label>
        </div>
        
        <button type="submit">Send Emails</button>
        <button type="button" id="previewBtn">Preview First Email</button>
    </form>
    
    <div id="status"></div>
    
    <script>
        document.getElementById('emailForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('csv', document.getElementById('csvFile').files[0]);
            formData.append('template', document.getElementById('templateFile').files[0]);
            formData.append('subject', document.getElementById('subject').value);
            formData.append('model', document.getElementById('model').value);
            formData.append('dry_run', document.getElementById('dryRun').checked);
            formData.append('use_llm', document.getElementById('useLLM').checked);
            
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<p>Sending emails...</p>';
            
            try {
                const response = await fetch('/api/send-emails', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = `<p>✅ ${result.message}</p>`;
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = `<p>❌ Error: ${result.error}</p>`;
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.innerHTML = `<p>❌ Error: ${error.message}</p>`;
            }
        });
        
        document.getElementById('previewBtn').addEventListener('click', async () => {
            // Implement preview functionality
            alert('Preview feature - to be implemented');
        });
    </script>
</body>
</html>
```

### Phase 3: Enhanced Features

**1. Job Queue (for large batches):**
```python
from celery import Celery

celery = Celery('mailerslave', broker='redis://localhost:6379')

@celery.task
def send_email_batch(csv_path, template_path, config):
    # Process in background
    pass
```

**2. Progress Tracking:**
```python
from flask_socketio import SocketIO

socketio = SocketIO(app)

@socketio.on('send_emails')
def handle_send(data):
    # Send progress updates
    emit('progress', {'percent': 50, 'message': 'Sending...'})
```

**3. Database for History:**
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    sent_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
```

## Project Structure After Web Extension

```
MailerSlave/
├── mailerslave/
│   ├── __init__.py
│   ├── cli.py              # CLI interface (existing)
│   ├── api.py              # NEW: REST API
│   ├── modules/            # Core modules (existing)
│   │   ├── csv_reader.py
│   │   ├── template_handler.py
│   │   ├── ollama_generator.py
│   │   ├── email_sender.py
│   │   └── config.py
│   ├── static/             # NEW: Frontend files
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   └── templates/          # NEW: Jinja2 templates
│       └── base.html
├── tests/
│   ├── test_modules.py     # Existing tests
│   └── test_api.py         # NEW: API tests
└── pyproject.toml
```

## Running the Web Service

Add to `pyproject.toml`:

```toml
[project.scripts]
mailerslave = "mailerslave.cli:main"
mailerslave-web = "mailerslave.api:main"  # NEW
```

Then run:

```bash
# CLI (existing)
mailerslave --csv emails.csv --template template.txt

# Web service (new)
mailerslave-web
# Or: python -m mailerslave.api
```

## Security Considerations

1. **Authentication:** Add user authentication
   ```python
   from flask_login import login_required
   
   @app.route('/api/send-emails')
   @login_required
   def send_emails():
       pass
   ```

2. **Rate Limiting:** Prevent abuse
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app)
   
   @app.route('/api/send-emails')
   @limiter.limit("10 per hour")
   def send_emails():
       pass
   ```

3. **File Validation:** Validate uploads
   ```python
   ALLOWED_EXTENSIONS = {'csv', 'txt'}
   
   def allowed_file(filename):
       return '.' in filename and \
              filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   ```

4. **Environment Variables:** Never expose credentials
   ```python
   # Keep using .env file
   # Never commit sensitive data
   ```

## Deployment

**Development:**
```bash
python -m mailerslave.api
```

**Production (Gunicorn):**
```bash
gunicorn mailerslave.api:app -w 4 -b 0.0.0.0:8000
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["gunicorn", "mailerslave.api:app", "-b", "0.0.0.0:8000"]
```

## Benefits of This Architecture

1. **Reusability:** Core modules work for both CLI and Web
2. **Testability:** Each layer can be tested independently
3. **Scalability:** Easy to add workers, queues, etc.
4. **Maintainability:** Clear separation of concerns
5. **Flexibility:** Can add more interfaces (GraphQL, gRPC, etc.)

## Next Steps

1. Implement basic Flask API
2. Create simple HTML frontend
3. Add file upload handling
4. Implement preview feature
5. Add job queue for large batches
6. Create progress tracking
7. Add user authentication
8. Deploy to cloud service

The modular design makes each step independent and testable!
