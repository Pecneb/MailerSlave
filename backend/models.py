"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


# Enums
class CampaignStatus(str, Enum):
    """Campaign status enum."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class EmailStatus(str, Enum):
    """Email log status enum."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


# Contact models
class ContactBase(BaseModel):
    """Base contact model."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    custom_fields: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    active: bool = True


class ContactCreate(ContactBase):
    """Contact creation model."""
    pass


class ContactUpdate(BaseModel):
    """Contact update model."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    custom_fields: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    active: Optional[bool] = None


class ContactResponse(ContactBase):
    """Contact response model."""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Template models
class TemplateBase(BaseModel):
    """Base template model."""
    name: str
    subject: str
    content: str
    description: Optional[str] = None
    placeholders: List[str] = Field(default_factory=list)
    use_llm: bool = False


class TemplateCreate(TemplateBase):
    """Template creation model."""
    pass


class TemplateUpdate(BaseModel):
    """Template update model."""
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    placeholders: Optional[List[str]] = None
    use_llm: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Template response model."""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Campaign models
class CampaignBase(BaseModel):
    """Base campaign model."""
    name: str
    template_id: str
    contact_ids: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    """Campaign creation model."""
    pass


class CampaignUpdate(BaseModel):
    """Campaign update model."""
    name: Optional[str] = None
    template_id: Optional[str] = None
    contact_ids: Optional[List[str]] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(CampaignBase):
    """Campaign response model."""
    id: str = Field(alias="_id")
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_emails: int = 0
    sent_count: int = 0
    failed_count: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Email log models
class EmailLogBase(BaseModel):
    """Base email log model."""
    campaign_id: str
    contact_id: str
    template_id: str
    subject: str
    body: str
    status: EmailStatus = EmailStatus.PENDING


class EmailLogCreate(EmailLogBase):
    """Email log creation model."""
    pass


class EmailLogResponse(EmailLogBase):
    """Email log response model."""
    id: str = Field(alias="_id")
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Dashboard models
class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_contacts: int
    total_templates: int
    total_campaigns: int
    active_campaigns: int
    total_emails_sent: int
    emails_sent_today: int
    recent_campaigns: List[CampaignResponse]
    recent_emails: List[EmailLogResponse]


# Bulk operations
class BulkContactImport(BaseModel):
    """Bulk contact import model."""
    contacts: List[ContactCreate]


class CampaignSendRequest(BaseModel):
    """Request to start sending a campaign."""
    dry_run: bool = False
