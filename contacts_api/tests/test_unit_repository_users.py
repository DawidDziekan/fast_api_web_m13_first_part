import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session
from fastapi import UploadFile
import asyncio

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repository import users
from src.database.models import User
from src.schemas import UserModel


class TestUsersRepository(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.user_data = UserModel(
            email="john@example.com",
            username="johndoe",
            password="securepwd",  # Adjusted to meet the max length constraint
            avatar=None  # You can mock the UploadFile object for testing avatar uploads
        )

    @patch('src.repository.users.cloudinary.uploader.upload', new_callable=AsyncMock)
    def test_create_user_without_avatar(self, mock_upload):
        mock_upload.return_value = {"url": "http://example.com/avatar.jpg"}
        asyncio.run(users.create_user(self.user_data, self.db))

        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    @patch('src.repository.users.cloudinary.uploader.upload', new_callable=AsyncMock)
    def test_create_user_with_avatar(self, mock_upload):
        avatar_file = MagicMock(spec=UploadFile)
        avatar_file.file = MagicMock()
        self.user_data.avatar = avatar_file
        mock_upload.return_value = {"url": "http://example.com/avatar.jpg"}
        
        asyncio.run(users.create_user(self.user_data, self.db))

        mock_upload.assert_called_once_with(avatar_file.file)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    def test_get_user_by_email(self):
        email = "john@example.com"
        mock_user = User(email=email, username="johndoe", password="securepwd")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        fetched_user = asyncio.run(users.get_user_by_email(email, self.db))
        
        self.db.query.assert_called_once_with(User)
        self.db.query.return_value.filter.assert_called_once()
        self.assertEqual(fetched_user, mock_user)

    def test_update_token(self):
        mock_user = User(email="john@example.com", username="johndoe", password="securepwd", refresh_token=None)
        token = "new_refresh_token"
        
        asyncio.run(users.update_token(mock_user, token, self.db))

        self.db.commit.assert_called_once()
        self.assertEqual(mock_user.refresh_token, token)

    def test_confirmed_email(self):
        email = "john@example.com"
        mock_user = User(email=email, username="johndoe", password="securepwd", confirmed=False)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        asyncio.run(users.confirmed_email(email, self.db))

        self.db.commit.assert_called_once()
        self.assertTrue(mock_user.confirmed)

if __name__ == '__main__':
    unittest.main()