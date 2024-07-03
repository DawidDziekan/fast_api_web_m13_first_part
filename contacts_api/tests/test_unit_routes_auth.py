import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from src.schemas import UserModel, RequestEmail
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

client = TestClient(app)

@pytest.fixture
def test_app():
    return TestClient(app)

@pytest.fixture
def user_model():
    return UserModel(
        email="john@example.com",
        username="johndoe",
        password="securepwd",
        confirmed=False
    )

@pytest.fixture
def user():
    return User(
        email="john@example.com",
        username="johndoe",
        password="hashed_pwd",
        confirmed=False
    )

@patch('src.repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('src.repository.users.create_user', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.get_password_hash', new_callable=AsyncMock)
@patch('src.services.email.send_email', new_callable=AsyncMock)
async def test_signup(mock_send_email, mock_get_password_hash, mock_create_user, mock_get_user_by_email, test_app, user_model):
    mock_get_user_by_email.return_value = None
    mock_create_user.return_value = user_model
    mock_get_password_hash.return_value = "hashed_pwd"

    response = test_app.post("/auth/signup", json=user_model.dict())

    assert response.status_code == 201
    assert response.json() == {"user": user_model.dict(), "detail": "User successfully created"}

@patch('src.repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.verify_password', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.create_access_token', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.create_refresh_token', new_callable=AsyncMock)
@patch('src.repository.users.update_token', new_callable=AsyncMock)
async def test_login(mock_update_token, mock_create_refresh_token, mock_create_access_token, mock_verify_password, mock_get_user_by_email, test_app, user):
    mock_get_user_by_email.return_value = user
    mock_verify_password.return_value = True
    mock_create_access_token.return_value = "access_token"
    mock_create_refresh_token.return_value = "refresh_token"

    response = test_app.post("/auth/login", json={"username": "john@example.com", "password": "securepwd"})  # Zmiana data na json

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "token_type": "bearer"
    }

@patch('src.repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.decode_refresh_token', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.create_access_token', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.create_refresh_token', new_callable=AsyncMock)
@patch('src.repository.users.update_token', new_callable=AsyncMock)
async def test_refresh_token(mock_update_token, mock_create_refresh_token, mock_create_access_token, mock_decode_refresh_token, mock_get_user_by_email, test_app, user):
    mock_decode_refresh_token.return_value = user.email
    mock_get_user_by_email.return_value = user
    mock_create_access_token.return_value = "new_access_token"
    mock_create_refresh_token.return_value = "new_refresh_token"

    headers = {"Authorization": "Bearer old_refresh_token"}
    response = test_app.get("/auth/refresh_token", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "bearer"
    }

@patch('src.repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('src.services.auth.auth_service.get_email_from_token', new_callable=AsyncMock)
@patch('src.repository.users.confirmed_email', new_callable=AsyncMock)
async def test_confirmed_email(mock_confirmed_email, mock_get_email_from_token, mock_get_user_by_email, test_app, user):
    mock_get_email_from_token.return_value = user.email
    mock_get_user_by_email.return_value = user

    response = test_app.get("/auth/confirmed_email/test_token")

    assert response.status_code == 200
    assert response.json() == {"message": "Email confirmed"}

@patch('src.repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('src.services.email.send_email', new_callable=AsyncMock)
async def test_request_email(mock_send_email, mock_get_user_by_email, test_app, user):
    mock_get_user_by_email.return_value = user

    response = test_app.post("/auth/request_email", json={"email": user.email})

    assert response.status_code == 200
    assert response.json() == {"message": "Check your email for confirmation."}

@patch('src.config.cloudinary.uploader.upload', new_callable=AsyncMock)
async def test_upload_avatar(mock_upload, test_app):
    mock_upload.return_value = {"url": "http://example.com/avatar.jpg"}

    avatar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_avatar.png'))
    with open(avatar_path, "rb") as f:
        response = test_app.post("/auth/upload-avatar/", files={"file": ("test_avatar.png", f, "image/png")})

    assert response.status_code == 200
    assert response.json() == {"url": "http://example.com/avatar.jpg"}

