"""Campaigns API routes."""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List
from bson import ObjectId
from datetime import datetime
import logging

from backend.models import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignStatus,
    CampaignSendRequest,
)
from backend.database import get_database
from backend.services.email_sender import AsyncEmailSender, DryRunEmailSender
from backend.services.ollama_service import OllamaService
from backend.services.template_service import TemplateService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(campaign: CampaignCreate):
    """Create a new email campaign."""
    db = get_database()
    
    # Validate template exists
    try:
        template = await db.templates.find_one({"_id": ObjectId(campaign.template_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid template ID")
    
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    # Validate contacts exist
    contact_objects = []
    for contact_id in campaign.contact_ids:
        try:
            contact = await db.contacts.find_one({"_id": ObjectId(contact_id)})
            if not contact:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Contact {contact_id} not found"
                )
            contact_objects.append(contact)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid contact ID: {contact_id}")
    
    campaign_dict = campaign.model_dump()
    campaign_dict["status"] = CampaignStatus.DRAFT.value
    campaign_dict["created_at"] = datetime.utcnow()
    campaign_dict["updated_at"] = datetime.utcnow()
    campaign_dict["total_emails"] = len(campaign.contact_ids)
    campaign_dict["sent_count"] = 0
    campaign_dict["failed_count"] = 0
    
    result = await db.campaigns.insert_one(campaign_dict)
    created_campaign = await db.campaigns.find_one({"_id": result.inserted_id})
    created_campaign["_id"] = str(created_campaign["_id"])
    
    return CampaignResponse(**created_campaign)


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(skip: int = 0, limit: int = 100, status_filter: str = None):
    """List all campaigns with pagination."""
    db = get_database()
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    cursor = db.campaigns.find(query).skip(skip).limit(limit).sort("created_at", -1)
    campaigns = await cursor.to_list(length=limit)
    
    for campaign in campaigns:
        campaign["_id"] = str(campaign["_id"])
    
    return [CampaignResponse(**campaign) for campaign in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str):
    """Get a specific campaign by ID."""
    db = get_database()
    
    try:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    campaign["_id"] = str(campaign["_id"])
    return CampaignResponse(**campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: str, campaign_update: CampaignUpdate):
    """Update a campaign."""
    db = get_database()
    
    try:
        existing = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    # Don't allow updates to campaigns that are in progress or completed
    if existing["status"] in [CampaignStatus.IN_PROGRESS.value, CampaignStatus.COMPLETED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update campaign that is in progress or completed"
        )
    
    update_data = campaign_update.model_dump(exclude_unset=True)
    
    # Update total_emails if contact_ids changed
    if "contact_ids" in update_data:
        update_data["total_emails"] = len(update_data["contact_ids"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": update_data}
    )
    
    updated_campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    updated_campaign["_id"] = str(updated_campaign["_id"])
    
    return CampaignResponse(**updated_campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: str):
    """Delete a campaign."""
    db = get_database()
    
    try:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    # Don't allow deletion of campaigns in progress
    if campaign["status"] == CampaignStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete campaign that is in progress"
        )
    
    await db.campaigns.delete_one({"_id": ObjectId(campaign_id)})


@router.post("/{campaign_id}/send", response_model=dict)
async def send_campaign(
    campaign_id: str,
    send_request: CampaignSendRequest,
    background_tasks: BackgroundTasks
):
    """Start sending emails for a campaign."""
    db = get_database()
    
    try:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid campaign ID")
    
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    # Check campaign status
    if campaign["status"] not in [CampaignStatus.DRAFT.value, CampaignStatus.PAUSED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot send campaign with status: {campaign['status']}"
        )
    
    # Update campaign status
    await db.campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "status": CampaignStatus.IN_PROGRESS.value,
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        }
    )
    
    # Start sending in background
    background_tasks.add_task(
        _send_campaign_emails,
        campaign_id=campaign_id,
        dry_run=send_request.dry_run
    )
    
    return {
        "message": "Campaign started",
        "campaign_id": campaign_id,
        "dry_run": send_request.dry_run
    }


async def _send_campaign_emails(campaign_id: str, dry_run: bool = False):
    """Background task to send campaign emails."""
    db = get_database()
    
    try:
        # Get campaign, template, and contacts
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        template = await db.templates.find_one({"_id": ObjectId(campaign["template_id"])})
        
        # Initialize email sender
        if dry_run:
            email_sender = DryRunEmailSender()
        else:
            email_sender = AsyncEmailSender()
        
        # Initialize Ollama if template uses LLM
        ollama_service = None
        if template.get("use_llm", False):
            ollama_service = OllamaService()
        
        sent_count = 0
        failed_count = 0
        
        # Send to each contact
        for contact_id in campaign["contact_ids"]:
            try:
                contact = await db.contacts.find_one({"_id": ObjectId(contact_id)})
                if not contact:
                    logger.warning(f"Contact {contact_id} not found, skipping")
                    failed_count += 1
                    continue
                
                # Prepare recipient data
                recipient_data = {
                    "email": contact["email"],
                    "first_name": contact.get("first_name", ""),
                    "last_name": contact.get("last_name", ""),
                    **contact.get("custom_fields", {})
                }
                
                # Generate or render email body
                if ollama_service:
                    body = await ollama_service.generate_email(
                        template["content"],
                        recipient_data
                    )
                else:
                    body = TemplateService.render_template(
                        template["content"],
                        recipient_data
                    )
                
                # Send email
                success, error = await email_sender.send_email(
                    to_email=contact["email"],
                    subject=template["subject"],
                    body=body,
                    log_to_db=True,
                    campaign_id=campaign_id,
                    contact_id=contact_id,
                    template_id=campaign["template_id"]
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    logger.error(f"Failed to send to {contact['email']}: {error}")
                
            except Exception as e:
                logger.error(f"Error sending to contact {contact_id}: {e}")
                failed_count += 1
        
        # Update campaign with final counts
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "status": CampaignStatus.COMPLETED.value,
                    "sent_count": sent_count,
                    "failed_count": failed_count,
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            }
        )
        
        logger.info(f"Campaign {campaign_id} completed: {sent_count} sent, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Fatal error in campaign {campaign_id}: {e}")
        # Mark campaign as failed
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "status": CampaignStatus.FAILED.value,
                    "updated_at": datetime.utcnow(),
                }
            }
        )
