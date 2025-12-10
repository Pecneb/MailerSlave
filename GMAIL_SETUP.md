# Gmail SMTP Setup Guide

## The Problem
Gmail error: `Username and Password not accepted`

**Reason:** Gmail blocks regular password authentication for security. You MUST use an **App Password**.

---

## Solution: Generate Gmail App Password

### Step 1: Enable 2-Factor Authentication (if not already)
1. Go to: https://myaccount.google.com/security
2. Click **2-Step Verification**
3. Follow steps to enable it (required for App Passwords)

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
   - Or Google Account → Security → 2-Step Verification → App passwords
2. Select:
   - **App:** Mail
   - **Device:** Other (Custom name) → "MailerSlave"
3. Click **Generate**
4. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 3: Update Your .env File
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop    # ← App Password (no spaces!)
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Important:** Remove spaces from the App Password!

### Step 4: Test It
```bash
python test_email.py
```

---

## Alternative: Use a Different Email Provider

### Option 1: Outlook/Office365
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

### Option 2: SendGrid (Recommended for bulk emails)
1. Sign up: https://sendgrid.com (free tier: 100 emails/day)
2. Create API key
3. Use:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_USE_TLS=true
```

### Option 3: Mailgun
1. Sign up: https://mailgun.com
2. Get SMTP credentials
3. Use them in .env

---

## Quick Diagnosis

Run the test script to see exactly what's wrong:
```bash
python test_email.py
```

It will test:
1. ✅ Connection to SMTP server
2. ✅ TLS encryption
3. ✅ Authentication
4. ✅ Send test email

---

## Common Issues

### "Username and Password not accepted"
→ You're using regular password instead of App Password
→ Solution: Generate App Password (see above)

### "Connection timed out"
→ Firewall blocking port 587
→ Try port 465 with SSL instead

### "Must issue STARTTLS first"
→ Set `SMTP_USE_TLS=true` in .env

### "Relay access denied"
→ Wrong username or FROM email doesn't match
→ Make sure `SMTP_FROM_EMAIL` matches `SMTP_USERNAME`

---

## Docker Users

After updating .env, restart containers:
```bash
docker-compose down
docker-compose up
```

Or just restart backend:
```bash
docker-compose restart backend
```

---

## Testing from Docker Container

If you want to test from inside the Docker container:
```bash
docker-compose exec backend python /app/test_email.py
```

(You may need to copy test_email.py to the backend/ directory first)
