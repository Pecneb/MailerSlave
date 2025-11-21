# MailerSlave v2.0

A modern full-stack email campaign management platform with FastAPI backend, Next.js frontend, and MongoDB database. Features AI-powered email personalization using Ollama LLM.

## 🚀 Features

- **📧 Campaign Management**: Create, manage, and track email campaigns
- **👥 Contact Management**: Store and organize email contacts with custom fields
- **📝 Template System**: Create reusable email templates with variable substitution
- **🤖 AI-Powered Personalization**: Use Ollama LLM to generate personalized email content
- **📊 Analytics Dashboard**: Real-time statistics and campaign tracking
- **📝 Email Logs**: Complete audit trail of all sent emails
- **🎨 Modern Web UI**: Beautiful Next.js frontend with Tailwind CSS
- **🔄 RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **💾 MongoDB Database**: Scalable NoSQL database for all data
- **🐳 Docker Support**: Easy deployment with Docker Compose
- **🧪 Dry Run Mode**: Test campaigns without sending real emails

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended) OR:
  - Python 3.11+
  - Node.js 20+
  - MongoDB 7.0+
- **Ollama** (optional, for AI-powered email generation)
- **SMTP Server Credentials** (e.g., Gmail App Password)

## 🏃 Quick Start with Docker

1. **Clone the repository**:
```bash
git clone https://github.com/Pecneb/MailerSlave.git
cd MailerSlave
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your SMTP credentials
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🛠️ Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if not using Docker)
# Make sure MongoDB is running on localhost:27017

# Configure environment
cp ../.env.example ../.env
# Edit .env with your configuration

# Run the backend
uvicorn backend.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if needed

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

## 📖 Usage Guide

### 1. Add Contacts

Navigate to **Contacts** page and click "Add Contact". You can:
- Add individual contacts manually
- Bulk import from CSV files

CSV format:
```csv
email,first_name,last_name,company,position
john@example.com,John,Doe,Acme Corp,Engineer
jane@example.com,Jane,Smith,Tech Co,Manager
```

### 2. Create Templates

Go to **Templates** page and create email templates with:
- Subject line
- Body content with variables: `$first_name`, `$company`, etc.
- Option to use AI generation (requires Ollama)

Example template:
```
Hi $first_name,

I hope this email finds you well at $company...

Best regards
```

### 3. Create Campaign

Navigate to **Campaigns** and click "New Campaign":
1. Enter campaign name and description
2. Select email template
3. Choose target contacts
4. Review and launch

### 4. Monitor Results

- **Dashboard**: View overall statistics and recent activity
- **Email Logs**: See detailed logs of all sent emails
- **Campaign Detail**: Track individual campaign progress

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=mailerslave

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com

# Ollama (optional)
OLLAMA_MODEL=llama2
OLLAMA_HOST=http://localhost:11434
OLLAMA_TEMPERATURE=0.7

# Application
DEBUG=false
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### SMTP Setup (Gmail Example)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account → Security → 2-Step Verification
   - Scroll to "App passwords"
   - Generate password for "Mail"
3. Use the generated password as `SMTP_PASSWORD`

## 🏗️ Architecture

```
MailerSlave/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── config.py           # Settings management
│   ├── database.py         # MongoDB connection
│   ├── models.py           # Pydantic models
│   ├── routes/             # API endpoints
│   │   ├── contacts.py
│   │   ├── templates.py
│   │   ├── campaigns.py
│   │   ├── emails.py
│   │   └── dashboard.py
│   └── services/           # Business logic
│       ├── email_sender.py
│       ├── ollama_service.py
│       └── template_service.py
│
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Dashboard
│   │   ├── contacts/
│   │   ├── templates/
│   │   ├── campaigns/
│   │   └── emails/
│   └── lib/               # Utilities
│       ├── api.ts         # API client
│       └── types.ts       # TypeScript types
│
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.backend      # Backend container
└── .env.example           # Environment template
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Contacts
- `GET /api/contacts` - List all contacts
- `POST /api/contacts` - Create contact
- `PUT /api/contacts/{id}` - Update contact
- `DELETE /api/contacts/{id}` - Delete contact
- `POST /api/contacts/bulk` - Bulk import

#### Templates
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template

#### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/{id}/send` - Start sending
- `GET /api/campaigns/{id}` - Get campaign details

#### Email Logs
- `GET /api/emails` - List email logs
- `GET /api/emails/campaign/{id}/stats` - Get campaign stats

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## 🧪 Testing

### Dry Run Mode

Test campaigns without sending real emails:

```bash
# In the UI, check "Dry Run" when sending a campaign

# Or via API:
curl -X POST http://localhost:8000/api/campaigns/{id}/send \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

## 🔒 Security Notes

- Never commit `.env` files to version control
- Use app-specific passwords for email accounts
- Rotate SMTP credentials regularly
- Consider using environment-specific configs for production

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆕 Migration from v1.x

The original CLI tool is preserved in the `mailerslave/` directory. To use the legacy CLI:

```bash
pip install -e .
mailerslave --csv emails.csv --template template.txt
```

The v2.0 web platform provides all CLI functionality plus:
- Web interface
- Database persistence
- Campaign management
- Analytics and tracking
- RESTful API

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Pecneb/MailerSlave/issues
- Documentation: See `docs/` directory

---

**Made with ❤️ for better email campaigns**
