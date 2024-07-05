import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import UploadFile

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repository import users
from src.database.models import User
from src.schemas import UserModel

@pytest.fixture
def db():
    return MagicMock()

@pytest.fixture
def user_data():
    return UserModel(
        email="john@example.com",
        username="johndoe",
        password="securepwd",
        avatar=None
    )

@pytest.mark.asyncio
async def test_create_user_without_avatar(db, user_data):
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    await users.create_user(user_data, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_with_avatar(db, user_data):
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    avatar_file = MagicMock(spec=UploadFile)
    avatar_file.file = MagicMock()
    user_data.avatar = avatar_file

    await users.create_user(user_data, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_email(db):
    email = "john@example.com"
    mock_user = User(email=email, username="johndoe", password="securepwd")
    db.query.return_value.filter.return_value.first.return_value = mock_user
    result = await users.get_user_by_email(email, db)
    
    assert result == mock_user


@pytest.mark.asyncio
async def test_update_token(db):
    mock_user = User(email="john@example.com", username="johndoe", password="securepwd", refresh_token=None)
    token = "new_refresh_token"
    db.commit = MagicMock()
    
    await users.update_token(mock_user, token, db)
    assert mock_user.refresh_token == token