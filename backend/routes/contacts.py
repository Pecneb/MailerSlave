"""Contacts API routes."""

from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from backend.models import ContactCreate, ContactUpdate, ContactResponse, BulkContactImport
from backend.database import get_database

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate):
    """Create a new contact."""
    db = get_database()
    
    # Check if email already exists
    existing = await db.contacts.find_one({"email": contact.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contact with email {contact.email} already exists"
        )
    
    contact_dict = contact.model_dump()
    contact_dict["created_at"] = datetime.utcnow()
    contact_dict["updated_at"] = datetime.utcnow()
    
    result = await db.contacts.insert_one(contact_dict)
    created_contact = await db.contacts.find_one({"_id": result.inserted_id})
    created_contact["_id"] = str(created_contact["_id"])
    
    return ContactResponse(**created_contact)


@router.get("/", response_model=List[ContactResponse])
async def list_contacts(skip: int = 0, limit: int = 100, active: bool = None):
    """List all contacts with pagination."""
    db = get_database()
    
    query = {}
    if active is not None:
        query["active"] = active
    
    cursor = db.contacts.find(query).skip(skip).limit(limit).sort("created_at", -1)
    contacts = await cursor.to_list(length=limit)
    
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    
    return [ContactResponse(**contact) for contact in contacts]


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str):
    """Get a specific contact by ID."""
    db = get_database()
    
    try:
        contact = await db.contacts.find_one({"_id": ObjectId(contact_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact ID")
    
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    contact["_id"] = str(contact["_id"])
    return ContactResponse(**contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: str, contact_update: ContactUpdate):
    """Update a contact."""
    db = get_database()
    
    # Get existing contact
    try:
        existing = await db.contacts.find_one({"_id": ObjectId(contact_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact ID")
    
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    # Check email uniqueness if email is being updated
    if contact_update.email and contact_update.email != existing["email"]:
        email_exists = await db.contacts.find_one({"email": contact_update.email})
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Contact with email {contact_update.email} already exists"
            )
    
    # Update fields
    update_data = contact_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.contacts.update_one(
        {"_id": ObjectId(contact_id)},
        {"$set": update_data}
    )
    
    updated_contact = await db.contacts.find_one({"_id": ObjectId(contact_id)})
    updated_contact["_id"] = str(updated_contact["_id"])
    
    return ContactResponse(**updated_contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: str):
    """Delete a contact."""
    db = get_database()
    
    try:
        result = await db.contacts.delete_one({"_id": ObjectId(contact_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


@router.post("/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def bulk_import_contacts(bulk_import: BulkContactImport):
    """Bulk import contacts from CSV or JSON."""
    db = get_database()
    
    created = 0
    skipped = 0
    errors = []
    
    for contact_data in bulk_import.contacts:
        try:
            # Check if exists
            existing = await db.contacts.find_one({"email": contact_data.email})
            if existing:
                skipped += 1
                continue
            
            contact_dict = contact_data.model_dump()
            contact_dict["created_at"] = datetime.utcnow()
            contact_dict["updated_at"] = datetime.utcnow()
            
            await db.contacts.insert_one(contact_dict)
            created += 1
            
        except Exception as e:
            errors.append({"email": contact_data.email, "error": str(e)})
    
    return {
        "created": created,
        "skipped": skipped,
        "errors": errors
    }
