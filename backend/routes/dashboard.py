"""Dashboard API routes."""

from fastapi import APIRouter
from datetime import datetime, timedelta

from backend.models import DashboardStats, CampaignResponse, EmailLogResponse, EmailStatus
from backend.database import get_database

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    db = get_database()
    
    # Count totals
    total_contacts = await db.contacts.count_documents({})
    total_templates = await db.templates.count_documents({})
    total_campaigns = await db.campaigns.count_documents({})
    active_campaigns = await db.campaigns.count_documents({"status": "in_progress"})
    total_emails_sent = await db.email_logs.count_documents({"status": EmailStatus.SENT.value})
    
    # Count emails sent today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    emails_sent_today = await db.email_logs.count_documents({
        "status": EmailStatus.SENT.value,
        "sent_at": {"$gte": today_start}
    })
    
    # Get recent campaigns (last 5)
    recent_campaigns_cursor = db.campaigns.find().sort("created_at", -1).limit(5)
    recent_campaigns_raw = await recent_campaigns_cursor.to_list(length=5)
    
    recent_campaigns = []
    for campaign in recent_campaigns_raw:
        campaign["_id"] = str(campaign["_id"])
        recent_campaigns.append(CampaignResponse(**campaign))
    
    # Get recent emails (last 10)
    recent_emails_cursor = db.email_logs.find().sort("created_at", -1).limit(10)
    recent_emails_raw = await recent_emails_cursor.to_list(length=10)
    
    recent_emails = []
    for email in recent_emails_raw:
        email["_id"] = str(email["_id"])
        recent_emails.append(EmailLogResponse(**email))
    
    return DashboardStats(
        total_contacts=total_contacts,
        total_templates=total_templates,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_emails_sent=total_emails_sent,
        emails_sent_today=emails_sent_today,
        recent_campaigns=recent_campaigns,
        recent_emails=recent_emails
    )
