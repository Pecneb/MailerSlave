# MailerSlave v2.0 - Quick Reference

## 🚀 Quick Start (Docker)

```bash
# 1. Setup
cp .env.example .env
nano .env  # Add your SMTP credentials

# 2. Start
./start.sh

# 3. Access
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📋 Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Restart after code changes
docker-compose restart backend
docker-compose restart frontend

# Rebuild containers
docker-compose up -d --build

# Remove everything (including database)
docker-compose down -v
```

## 🔧 Manual Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### MongoDB
```bash
# Install MongoDB locally or use Docker:
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

## 📁 Project Structure

```
backend/          - FastAPI application
  routes/         - API endpoints
  services/       - Business logic
  main.py         - App entry point
  models.py       - Data models
  
frontend/         - Next.js application
  app/            - Pages (App Router)
  lib/            - API client & types
  
docker-compose.yml - Service orchestration
.env              - Configuration (create from .env.example)
```

## 🔑 Environment Variables

### Required (Backend)
```env
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Optional
```env
MONGODB_URL=mongodb://localhost:27017
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
```

## 📝 Typical Workflow

1. **Add Contacts**
   - Navigate to Contacts
   - Click "Add Contact" or bulk import CSV
   
2. **Create Template**
   - Go to Templates
   - Create template with variables: `$first_name`, `$company`
   - Enable "Use LLM" for AI generation (optional)
   
3. **Create Campaign**
   - Navigate to Campaigns
   - Click "New Campaign"
   - Select template and contacts
   - Review and send
   
4. **Monitor Results**
   - Dashboard shows overall stats
   - Email Logs shows detailed results
   - Campaign detail shows progress

## 🧪 Testing

```bash
# Test with dry run mode
# In UI: Check "Dry Run" when sending campaign

# Test SMTP connection
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/api/contacts

# View API docs
open http://localhost:8000/docs
```

## 📊 API Examples

```bash
# List contacts
curl http://localhost:8000/api/contacts

# Create contact
curl -X POST http://localhost:8000/api/contacts \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "first_name": "Test"}'

# Send campaign
curl -X POST http://localhost:8000/api/campaigns/{id}/send \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats
```

## 🐛 Troubleshooting

### Backend won't start
- Check MongoDB is running: `docker ps | grep mongo`
- Check .env file exists and has SMTP credentials
- View logs: `docker-compose logs backend`

### Frontend won't start
- Check Node.js version: `node --version` (need 20+)
- Clear cache: `rm -rf frontend/.next frontend/node_modules`
- Reinstall: `cd frontend && npm install`

### Can't send emails
- Verify SMTP credentials in .env
- For Gmail: Use App Password (not regular password)
- Test in dry run mode first

### MongoDB connection failed
- Ensure MongoDB is running on port 27017
- Check MONGODB_URL in .env
- Try: `docker-compose restart mongodb`

### TypeScript errors in VS Code
- Normal during initial setup
- Run: `cd frontend && npm install`
- Restart VS Code

## 📚 Additional Resources

- Full documentation: `README_v2.md`
- Architecture details: `docs/ARCHITECTURE_V2.md`
- Refactor summary: `REFACTOR_SUMMARY.md`
- API documentation: http://localhost:8000/docs (when running)
- Original CLI: `mailerslave --help`

## 💡 Tips

1. **Start with dry run**: Always test campaigns with dry_run=true first
2. **Use variables**: `$first_name`, `$company`, etc. in templates
3. **Monitor logs**: Check email_logs for failures
4. **Backup database**: Export MongoDB data regularly
5. **Customize**: The codebase is modular and easy to extend

## 🔒 Production Checklist

- [ ] Set strong SMTP credentials
- [ ] Use production SMTP service (SendGrid, AWS SES)
- [ ] Add user authentication
- [ ] Set up MongoDB replica set
- [ ] Enable HTTPS/SSL
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Regular database backups
- [ ] Use environment-specific configs
- [ ] Review security best practices

## 📞 Support

- Issues: https://github.com/Pecneb/MailerSlave/issues
- Original CLI: Run `mailerslave --help`
- API Docs: http://localhost:8000/docs

---

**Quick Start Summary:**
```bash
cp .env.example .env
nano .env  # Add SMTP credentials
./start.sh
open http://localhost:3000
```

Happy emailing! 📧
