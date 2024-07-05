import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from src.database.models import User
from src.database.db import SessionLocal


class TestAuthRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.user = {
            "email": "john@example1234.com",
            "username": "asdfghjkl",
            "password": "zaq1@WSX"
        }

    def _get_session(self):
        return SessionLocal()

    @patch("src.routes.auth.send_email")
    def test_create_user(self, mock_send_email):
        session = self._get_session()
        user = session.query(User).filter_by(email=self.user["email"]).first()
        if user:
            session.delete(user)
            session.commit()
        
        response = self.client.post(
            "/api/auth/signup",
            json=self.user,
        )
        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertEqual(data["user"]["email"], self.user.get("email"))
        self.assertIn("id", data["user"])

    def test_repeat_create_user(self):
        self.client.post("/api/auth/signup", json=self.user)

        response = self.client.post(
            "/api/auth/signup",
            json=self.user,
        )
        self.assertEqual(response.status_code, 409, response.text)
        data = response.json()
        self.assertEqual(data["detail"], "Account already exists")

    def test_login_user_not_confirmed(self):
        session = self._get_session()
        user = session.query(User).filter_by(email=self.user["email"]).first()
        if user:
            user.confirmed = False
            session.commit()
        
        response = self.client.post(
            "/api/auth/login",
            data={"username": self.user.get('email'), "password": self.user.get('password')},
        )
        self.assertEqual(response.status_code, 401, response.text)
        data = response.json()
        self.assertEqual(data["detail"], "Email not confirmed")

    def test_login_user(self):
        session = self._get_session()
        current_user: User = session.query(User).filter(User.email == self.user.get('email')).first()
        if current_user:
            current_user.confirmed = True
            session.commit()
        else:
            self.fail("User does not exist in the database")

        response = self.client.post(
            "/api/auth/login",
            data={"username": self.user.get('email'), "password": self.user.get('password')},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["token_type"], "bearer")

    def test_login_wrong_password(self):
        session = self._get_session()
        current_user: User = session.query(User).filter(User.email == self.user.get('email')).first()
        if current_user:
            current_user.confirmed = True
            session.commit()
        else:
            self.fail("User does not exist in the database")
        
        response = self.client.post(
            "/api/auth/login",
            data={"username": self.user.get('email'), "password": 'wrong_password'},
        )
        self.assertEqual(response.status_code, 401, response.text)
        data = response.json()
        self.assertEqual(data["detail"], "Invalid password")

    def test_login_wrong_email(self):
        response = self.client.post(
            "/api/auth/login",
            data={"username": 'wrong_email@example.com', "password": self.user.get('password')},
        )
        self.assertEqual(response.status_code, 401, response.text)
        data = response.json()
        self.assertEqual(data["detail"], "Invalid email")

if __name__ == '__main__':
    unittest.main()

