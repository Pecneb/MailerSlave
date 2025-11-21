# MailerSlave v2.0 Architecture

## Overview

MailerSlave v2.0 is a complete refactor from a CLI tool to a modern full-stack web application. The architecture follows best practices with clear separation of concerns.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation and settings management
- **Ollama**: LLM integration for AI-powered email generation

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **TanStack Query**: Data fetching and caching
- **Axios**: HTTP client

### Database
- **MongoDB**: NoSQL database for flexible document storage

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **Uvicorn**: ASGI server for FastAPI

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                       Frontend                          │
│              Next.js 14 (Port 3000)                    │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │Dashboard │  │Contacts  │  │Templates │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐                           │
│  │Campaigns │  │  Logs    │                           │
│  └──────────┘  └──────────┘                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP REST API
                      │ (JSON)
┌─────────────────────▼───────────────────────────────────┐
│                    Backend API                          │
│              FastAPI (Port 8000)                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │              API Routes                          │ │
│  │  /contacts  /templates  /campaigns  /emails     │ │
│  └────────────┬─────────────────────────────────────┘ │
│               │                                        │
│  ┌────────────▼──────────────────────────────────┐   │
│  │           Business Logic Services             │   │
│  │  • Email Sender (SMTP)                        │   │
│  │  • Ollama Service (LLM)                       │   │
│  │  • Template Renderer                          │   │
│  └────────────┬──────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────┐
│                    MongoDB                           │
│              Database (Port 27017)                   │
│                                                      │
│  Collections:                                        │
│  • contacts      - Email recipients                  │
│  • templates     - Email templates                   │
│  • campaigns     - Campaign metadata                 │
│  • email_logs    - Sent email audit trail           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│            External Services                         │
│                                                      │
│  • SMTP Server (Gmail, SendGrid, etc.)              │
│  • Ollama API (Optional, for AI generation)         │
└──────────────────────────────────────────────────────┘
```

## Data Models

### Contact
```python
{
  "_id": ObjectId,
  "email": str,
  "first_name": str,
  "last_name": str,
  "custom_fields": dict,
  "tags": list[str],
  "active": bool,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Template
```python
{
  "_id": ObjectId,
  "name": str,
  "subject": str,
  "content": str,
  "description": str,
  "placeholders": list[str],
  "use_llm": bool,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Campaign
```python
{
  "_id": ObjectId,
  "name": str,
  "template_id": str,
  "contact_ids": list[str],
  "description": str,
  "status": enum,  # draft, in_progress, completed, failed, paused
  "created_at": datetime,
  "updated_at": datetime,
  "started_at": datetime,
  "completed_at": datetime,
  "total_emails": int,
  "sent_count": int,
  "failed_count": int
}
```

### Email Log
```python
{
  "_id": ObjectId,
  "campaign_id": str,
  "contact_id": str,
  "template_id": str,
  "subject": str,
  "body": str,
  "status": enum,  # pending, sent, failed, bounced
  "sent_at": datetime,
  "error_message": str,
  "created_at": datetime
}
```

## API Endpoints

### Contacts
- `GET /api/contacts` - List contacts (pagination, filtering)
- `POST /api/contacts` - Create contact
- `GET /api/contacts/{id}` - Get contact details
- `PUT /api/contacts/{id}` - Update contact
- `DELETE /api/contacts/{id}` - Delete contact
- `POST /api/contacts/bulk` - Bulk import contacts

### Templates
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `GET /api/templates/{id}` - Get template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template

### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaigns/{id}` - Get campaign
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign
- `POST /api/campaigns/{id}/send` - Start sending campaign

### Email Logs
- `GET /api/emails` - List email logs (filtering by campaign, contact, status, date)
- `GET /api/emails/{id}` - Get email log details
- `GET /api/emails/campaign/{id}/stats` - Get campaign statistics

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Email Sending Flow

```
1. User creates campaign
   ↓
2. Selects template and contacts
   ↓
3. Clicks "Send Campaign"
   ↓
4. Backend creates campaign record (status: in_progress)
   ↓
5. Background task starts
   ↓
6. For each contact:
   a. Fetch contact data
   b. If template.use_llm:
      - Call Ollama API to generate personalized content
   c. Else:
      - Render template with variable substitution
   d. Send email via SMTP
   e. Log result to email_logs collection
   f. Update campaign counts
   ↓
7. Campaign completed (status: completed)
   ↓
8. User views results in dashboard/logs
```

## Security Considerations

1. **Environment Variables**: Sensitive data (SMTP passwords) stored in .env files
2. **Input Validation**: Pydantic models validate all API inputs
3. **Email Validation**: Email addresses validated on input
4. **Rate Limiting**: Consider adding rate limiting for production
5. **Authentication**: Current version has no auth - add JWT/OAuth for production
6. **CORS**: Configured to allow Next.js frontend origin

## Scalability

### Current Architecture
- Suitable for small to medium workloads
- Background task processing in FastAPI
- Single MongoDB instance

### Production Improvements
1. **Task Queue**: Replace background tasks with Celery + Redis
2. **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
3. **MongoDB Replica Set**: For high availability
4. **Caching**: Add Redis for API response caching
5. **CDN**: Serve frontend assets from CDN
6. **Monitoring**: Add Prometheus + Grafana
7. **Authentication**: Add user management and JWT tokens

## Development vs Production

### Development
- Docker Compose for all services
- Hot reload enabled
- Debug logs enabled
- Local SMTP testing

### Production
- Kubernetes or cloud platform (AWS ECS, GCP Cloud Run)
- Environment-specific configs
- Production-grade SMTP service (SendGrid, AWS SES)
- SSL/TLS certificates
- Database backups
- Log aggregation (ELK stack)

## Migration from v1.x

The original CLI functionality is preserved in the `mailerslave/` directory. Key differences:

| Feature | v1.x (CLI) | v2.0 (Web) |
|---------|-----------|------------|
| Interface | Command line | Web UI + REST API |
| Data Storage | CSV files | MongoDB database |
| Email Tracking | Console logs | Database logs + UI |
| Campaign Management | Manual script runs | Campaign scheduler |
| User Management | N/A | Ready for multi-user |
| Analytics | Summary report | Real-time dashboard |
| Deployment | Python package | Docker containers |

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Email scheduling (cron-like)
- [ ] Email open/click tracking
- [ ] Template editor with preview
- [ ] CSV upload UI for bulk import
- [ ] Campaign duplication
- [ ] Contact segmentation and tagging
- [ ] A/B testing for templates
- [ ] Webhook notifications
- [ ] Export campaign results
