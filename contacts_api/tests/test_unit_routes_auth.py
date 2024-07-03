import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
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
    )

@pytest.fixture
def user():
    return User(
        email="john@example.com",
        username="johndoe",
        password="hashed_pwd",
    )

@patch('src.repository.users.get_user_by_email', AsyncMock())
@patch('src.repository.users.create_user', AsyncMock())
@patch('src.services.auth.auth_service.get_password_hash', AsyncMock())
@patch('src.services.email.send_email', AsyncMock())
def test_signup(test_app, user_model):
    response = test_app.post("/api/auth/signup", json=user_model.dict())

    assert response.status_code == 201
    assert response.json() == {"user": user_model.dict(), "detail": "User successfully created"}

@patch('src.repository.users.get_user_by_email', AsyncMock())
@patch('src.services.auth.auth_service.verify_password', AsyncMock())
@patch('src.services.auth.auth_service.create_access_token', AsyncMock())
@patch('src.services.auth.auth_service.create_refresh_token', AsyncMock())
@patch('src.repository.users.update_token', AsyncMock())
def test_login(test_app, user):
    response = test_app.post("/api/auth/login", json={"username": "john@example.com", "password": "securepwd"})

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "token_type": "bearer"
    }

@patch('src.repository.users.get_user_by_email', AsyncMock())
@patch('src.services.auth.auth_service.decode_refresh_token', AsyncMock())
@patch('src.services.auth.auth_service.create_access_token', AsyncMock())
@patch('src.services.auth.auth_service.create_refresh_token', AsyncMock())
@patch('src.repository.users.update_token', AsyncMock())
def test_refresh_token(test_app, user):
    headers = {"Authorization": "Bearer old_refresh_token"}
    response = test_app.get("/api/auth/refresh_token", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "bearer"
    }

@patch('src.repository.users.get_user_by_email', AsyncMock())
@patch('src.services.auth.auth_service.get_email_from_token', AsyncMock())
@patch('src.repository.users.confirmed_email', AsyncMock())
def test_confirmed_email(test_app, user):
    response = test_app.get("/api/auth/confirmed_email/test_token")

    assert response.status_code == 200
    assert response.json() == {"message": "Email confirmed"}

@patch('src.repository.users.get_user_by_email', AsyncMock())
@patch('src.services.email.send_email', AsyncMock())
def test_request_email(test_app, user):
    response = test_app.post("/api/auth/request_email", json={"email": user.email})

    assert response.status_code == 200
    assert response.json() == {"message": "Check your email for confirmation."}
