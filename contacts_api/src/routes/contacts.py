from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import models
from src.repository import contacts
from src import schemas
from src.database import db
from typing import List
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/", response_model=schemas.Contact, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(db.get_db), current_user: schemas.UserDb = Depends(auth_service.get_current_user)):
    """
    Create a new contact for the current user.
    
    - **contact**: JSON body containing contact details.
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with the created contact details.
    
    Raises:
    - HTTPException: If the contact limit for the user is reached.
    """
    contact_count = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).count()
    if contact_count >= 10:
        raise HTTPException(status_code=400, detail="Contact limit reached")
    return contacts.create_contact(db, contact, current_user.id)

@router.get("/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(db.get_db), current_user: schemas.UserDb = Depends(auth_service.get_current_user)):
    """
    Read a list of contacts for the current user.
    
    - **skip**: Number of records to skip (pagination).
    - **limit**: Maximum number of records to return (pagination).
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with a list of contacts.
    """
    return contacts.get_contacts(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(db.get_db)):
    """
    Read a specific contact by its ID.
    
    - **contact_id**: ID of the contact to retrieve.
    - **db**: SQLAlchemy database session dependency.
    
    Returns:
    - JSON response with the contact details.
    """
    return contacts.get_contact(db=db, contact_id=contact_id)

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(db.get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Update a specific contact by its ID.
    
    - **contact_id**: ID of the contact to update.
    - **contact**: JSON body containing updated contact details.
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with the updated contact details.
    
    Raises:
    - HTTPException: If the contact is not found or does not belong to the current user.
    """
    updated_contact = contacts.update_contact(db, contact_id, contact)
    if updated_contact is None or updated_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Delete a specific contact by its ID.
    
    - **contact_id**: ID of the contact to delete.
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with the deleted contact details.
    
    Raises:
    - HTTPException: If the contact is not found or does not belong to the current user.
    """
    deleted_contact = contacts.delete_contact(db, contact_id)
    if deleted_contact is None or deleted_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact

@router.get("/search/", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(db.get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Search for contacts by query string in first name, last name, or email.
    
    - **query**: Search query string.
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with a list of contacts matching the search criteria.
    """
    contacts = db.query(models.Contact).filter(
        models.Contact.first_name.contains(query) |
        models.Contact.last_name.contains(query) |
        models.Contact.email.contains(query),
        models.Contact.owner_id == current_user.id
    ).all()
    return contacts

@router.get("/birthdays/", response_model=List[schemas.Contact])
def upcoming_birthdays(db: Session = Depends(db.get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with upcoming birthdays within the next 7 days.
    
    - **db**: SQLAlchemy database session dependency.
    - **current_user**: The current authenticated user.
    
    Returns:
    - JSON response with a list of contacts having birthdays within the next 7 days.
    """
    today = datetime.today().date()
    upcoming_date = today + timedelta(days=7)
    contacts = db.query(models.Contact).filter(
        models.Contact.birthday.between(today, upcoming_date),
        models.Contact.owner_id == current_user.id
    ).all()
    return contacts