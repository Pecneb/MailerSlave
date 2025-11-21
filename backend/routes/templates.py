"""Templates API routes."""

from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from backend.models import TemplateCreate, TemplateUpdate, TemplateResponse
from backend.database import get_database
from backend.services.template_service import TemplateService

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreate):
    """Create a new email template."""
    db = get_database()
    
    # Extract placeholders from template content
    placeholders = TemplateService.extract_placeholders(template.content)
    
    template_dict = template.model_dump()
    template_dict["placeholders"] = placeholders
    template_dict["created_at"] = datetime.utcnow()
    template_dict["updated_at"] = datetime.utcnow()
    
    result = await db.templates.insert_one(template_dict)
    created_template = await db.templates.find_one({"_id": result.inserted_id})
    created_template["_id"] = str(created_template["_id"])
    
    return TemplateResponse(**created_template)


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(skip: int = 0, limit: int = 100):
    """List all templates with pagination."""
    db = get_database()
    
    cursor = db.templates.find().skip(skip).limit(limit).sort("created_at", -1)
    templates = await cursor.to_list(length=limit)
    
    for template in templates:
        template["_id"] = str(template["_id"])
    
    return [TemplateResponse(**template) for template in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template by ID."""
    db = get_database()
    
    try:
        template = await db.templates.find_one({"_id": ObjectId(template_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid template ID")
    
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    template["_id"] = str(template["_id"])
    return TemplateResponse(**template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, template_update: TemplateUpdate):
    """Update a template."""
    db = get_database()
    
    try:
        existing = await db.templates.find_one({"_id": ObjectId(template_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid template ID")
    
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    update_data = template_update.model_dump(exclude_unset=True)
    
    # Re-extract placeholders if content is updated
    if "content" in update_data:
        update_data["placeholders"] = TemplateService.extract_placeholders(update_data["content"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.templates.update_one(
        {"_id": ObjectId(template_id)},
        {"$set": update_data}
    )
    
    updated_template = await db.templates.find_one({"_id": ObjectId(template_id)})
    updated_template["_id"] = str(updated_template["_id"])
    
    return TemplateResponse(**updated_template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str):
    """Delete a template."""
    db = get_database()
    
    try:
        result = await db.templates.delete_one({"_id": ObjectId(template_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid template ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
