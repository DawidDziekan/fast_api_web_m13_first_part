from typing import Union
import cloudinary.uploader
from sqlalchemy.orm import Session
from fastapi import UploadFile
from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
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
