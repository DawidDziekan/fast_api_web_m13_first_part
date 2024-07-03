"""
This module provides functionality for managing user entities in the application. It includes operations such as retrieving a user by email and creating a new user.

Functions:
- get_user_by_email: Fetches a user from the database based on their email address.
- create_user: Registers a new user in the database, including uploading an avatar image if provided.

Dependencies:
- cloudinary.uploader: Used for uploading avatar images to Cloudinary.
- sqlalchemy.orm.Session: Used for database session management.
- fastapi.UploadFile: Represents a file uploaded by a client.
"""

from typing import Union
import cloudinary.uploader
from sqlalchemy.orm import Session
from fastapi import UploadFile
from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by their email address.

    Parameters:
    - email: The email address of the user to retrieve.
    - db: The database session.

    Returns:
    - A User object if found, None otherwise.
    """
    
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database. If an avatar image is provided, it uploads the image to Cloudinary and stores the URL.

    Parameters:
    - body: The user data (email, username, password, avatar).
    - db: The database session.

    Returns:
    - The newly created User object.
    """
    
    avatar_url = None
    if body.avatar:
        try:
            result = cloudinary.uploader.upload(body.avatar.file)
            avatar_url = result.get("url")
        except Exception as e:
            print(e)
            avatar_url = None
    new_user = User(
        email=body.email,
        username=body.username,
        password=body.password,
        avatar=avatar_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: Union[str, None], db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
