import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repository import contacts
from src.database import models
from src.schemas import ContactCreate, ContactUpdate

class TestContactsRepository(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="1234567890",
            birthday="1990-01-01"
        )
        self.contact_update_data = ContactUpdate(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone_number="0987654321",
            birthday="1991-02-02"
        )

    def test_create_contact(self):
        user_id = 1
        result_contact = models.Contact(**self.contact_data.model_dump(), owner_id=user_id)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None
        
        created_contact = contacts.create_contact(self.db, self.contact_data, user_id)
        
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(created_contact.owner_id, user_id)
        self.assertEqual(created_contact.first_name, self.contact_data.first_name)
        self.assertEqual(created_contact.last_name, self.contact_data.last_name)
        self.assertEqual(created_contact.email, self.contact_data.email)
        self.assertEqual(created_contact.phone_number, self.contact_data.phone_number)
        self.assertEqual(created_contact.birthday, self.contact_data.birthday)

    def test_get_contacts(self):
        user_id = 1
        mock_contacts = [models.Contact(id=i, first_name=f"Contact {i}", last_name=f"Last {i}", owner_id=user_id) for i in range(10)]
        self.db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_contacts
        
        contacts_list = contacts.get_contacts(self.db, user_id, skip=0, limit=10)
        
        self.db.query.assert_called_once_with(models.Contact)
        self.db.query.return_value.filter.assert_called_once()
        self.assertEqual(contacts_list, mock_contacts)

    def test_get_contact(self):
        contact_id = 1
        mock_contact = models.Contact(id=contact_id, first_name="Contact", last_name="1", owner_id=1)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        
        fetched_contact = contacts.get_contact(self.db, contact_id)
        
        self.db.query.assert_called_once_with(models.Contact)
        self.db.query.return_value.filter.assert_called_once()
        self.assertEqual(fetched_contact, mock_contact)

    def test_update_contact(self):
        contact_id = 1
        mock_contact = models.Contact(id=contact_id, first_name="Contact", last_name="1", owner_id=1)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        
        updated_contact = contacts.update_contact(self.db, contact_id, self.contact_update_data)
        
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(updated_contact.first_name, self.contact_update_data.first_name)
        self.assertEqual(updated_contact.last_name, self.contact_update_data.last_name)
        self.assertEqual(updated_contact.email, self.contact_update_data.email)
        self.assertEqual(updated_contact.phone_number, self.contact_update_data.phone_number)
        self.assertEqual(updated_contact.birthday, self.contact_update_data.birthday)

    def test_delete_contact(self):
        contact_id = 1
        mock_contact = models.Contact(id=contact_id, first_name="Contact", last_name="1", owner_id=1)
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        
        deleted_contact = contacts.delete_contact(self.db, contact_id)
        
        self.db.query.assert_called_once_with(models.Contact)
        self.db.query.return_value.filter.assert_called_once()
        self.db.delete.assert_called_once_with(mock_contact)
        self.db.commit.assert_called_once()
        self.assertEqual(deleted_contact, mock_contact)

if __name__ == '__main__':
    unittest.main()

