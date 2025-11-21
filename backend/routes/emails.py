"""Email logs API routes."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from backend.models import EmailLogResponse, EmailStatus
from backend.database import get_database

router = APIRouter()


@router.get("/", response_model=List[EmailLogResponse])
async def list_email_logs(
    skip: int = 0,
    limit: int = 100,
    campaign_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    days: int = 30
):
    """List email logs with filtering options."""
    db = get_database()
    
    # Build query
    query = {}
    
    if campaign_id:
        try:
            query["campaign_id"] = campaign_id
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if contact_id:
        try:
            query["contact_id"] = contact_id
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact ID")
    
    if status_filter:
        query["status"] = status_filter
    
    # Filter by date range
    if days > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query["created_at"] = {"$gte": cutoff_date}
    
    cursor = db.email_logs.find(query).skip(skip).limit(limit).sort("created_at", -1)
    logs = await cursor.to_list(length=limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return [EmailLogResponse(**log) for log in logs]


@router.get("/{log_id}", response_model=EmailLogResponse)
async def get_email_log(log_id: str):
    """Get a specific email log by ID."""
    db = get_database()
    
    try:
        log = await db.email_logs.find_one({"_id": ObjectId(log_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid log ID")
    
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email log not found")
    
    log["_id"] = str(log["_id"])
    return EmailLogResponse(**log)


@router.get("/campaign/{campaign_id}/stats", response_model=dict)
async def get_campaign_stats(campaign_id: str):
    """Get statistics for a specific campaign."""
    db = get_database()
    
    # Validate campaign exists
    try:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    # Count emails by status
    total = await db.email_logs.count_documents({"campaign_id": campaign_id})
    sent = await db.email_logs.count_documents({"campaign_id": campaign_id, "status": EmailStatus.SENT.value})
    failed = await db.email_logs.count_documents({"campaign_id": campaign_id, "status": EmailStatus.FAILED.value})
    pending = await db.email_logs.count_documents({"campaign_id": campaign_id, "status": EmailStatus.PENDING.value})
    
    return {
        "campaign_id": campaign_id,
        "total": total,
        "sent": sent,
        "failed": failed,
        "pending": pending,
        "success_rate": (sent / total * 100) if total > 0 else 0
    }
