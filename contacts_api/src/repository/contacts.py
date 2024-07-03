"""
This module provides CRUD operations for managing contacts in the database.

Functions:
- create_contact: Adds a new contact to the database for a specific user.
- get_contacts: Retrieves a list of contacts for a specific user, with optional pagination.
- get_contact: Fetches a single contact by its ID.
- update_contact: Updates the details of an existing contact.
- delete_contact: Removes a contact from the database by its ID.
"""

from sqlalchemy.orm import Session
from src.database import models
from src import schemas

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Creates a new contact associated with a user.

    Parameters:
    - db: Database session.
    - contact: Contact information to be created (schemas.ContactCreate).
    - user_id: ID of the user who owns the contact.

    Returns:
    - The newly created contact object.
    """
    db_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieves contacts for a specific user, with support for pagination.

    Parameters:
    - db: Database session.
    - user_id: ID of the user whose contacts are to be retrieved.
    - skip: Number of records to skip (for pagination).
    - limit: Maximum number of records to return.

    Returns:
    - A list of contacts.
    """
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    """
    Fetches a single contact by its ID.

    Parameters:
    - db: Database session.
    - contact_id: ID of the contact to retrieve.

    Returns:
    - The contact object if found, None otherwise.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    """
    Updates an existing contact.

    Parameters:
    - db: Database session.
    - contact_id: ID of the contact to update.
    - contact: New contact information (schemas.ContactUpdate).

    Returns:
    - The updated contact object.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    """
    Deletes a contact from the database.

    Parameters:
    - db: Database session.
    - contact_id: ID of the contact to delete.

    Returns:
    - None
    """
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
        return contact
    return None