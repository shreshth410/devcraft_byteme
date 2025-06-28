"""
Unit tests for Database Manager
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for Database Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_campus_copilot.db")
        self.db_manager = DatabaseManager(db_path=self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Database file should be created
        self.assertTrue(os.path.exists(self.test_db_path))
        
        # Tables should be created
        tables = self.db_manager.get_table_names()
        expected_tables = ["users", "college_events", "reminders", "user_settings"]
        
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_user_operations(self):
        """Test user CRUD operations"""
        # Create user
        user_id = 12345
        username = "test_user"
        full_name = "Test User"
        
        self.db_manager.create_user(user_id, username, full_name)
        
        # Get user
        user = self.db_manager.get_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)  # username column
        self.assertEqual(user[2], full_name)  # full_name column
        
        # Update user
        new_full_name = "Updated Test User"
        self.db_manager.update_user(user_id, full_name=new_full_name)
        
        updated_user = self.db_manager.get_user(user_id)
        self.assertEqual(updated_user[2], new_full_name)
        
        # Delete user
        self.db_manager.delete_user(user_id)
        deleted_user = self.db_manager.get_user(user_id)
        self.assertIsNone(deleted_user)
    
    def test_event_operations(self):
        """Test event CRUD operations"""
        # Create event
        event_data = {
            "title": "Test Event",
            "description": "This is a test event",
            "start_time": "2024-04-20 18:00:00",
            "end_time": "2024-04-20 20:00:00",
            "location": "Test Location",
            "category": "academic"
        }
        
        event_id = self.db_manager.create_event(**event_data)
        self.assertIsNotNone(event_id)
        
        # Get event
        event = self.db_manager.get_event(event_id)
        self.assertIsNotNone(event)
        self.assertEqual(event[1], event_data["title"])  # title column
        
        # Update event
        new_title = "Updated Test Event"
        self.db_manager.update_event(event_id, title=new_title)
        
        updated_event = self.db_manager.get_event(event_id)
        self.assertEqual(updated_event[1], new_title)
        
        # Get events by date range
        events = self.db_manager.get_events_by_date_range("2024-04-20", "2024-04-21")
        self.assertTrue(len(events) > 0)
        
        # Delete event
        self.db_manager.delete_event(event_id)
        deleted_event = self.db_manager.get_event(event_id)
        self.assertIsNone(deleted_event)
    
    def test_reminder_operations(self):
        """Test reminder CRUD operations"""
        # First create a user
        user_id = 12345
        self.db_manager.create_user(user_id, "test_user", "Test User")
        
        # Create reminder
        reminder_data = {
            "user_id": user_id,
            "title": "Test Reminder",
            "description": "This is a test reminder",
            "reminder_time": "2024-04-20 17:00:00",
            "is_recurring": False
        }
        
        reminder_id = self.db_manager.create_reminder(**reminder_data)
        self.assertIsNotNone(reminder_id)
        
        # Get reminder
        reminder = self.db_manager.get_reminder(reminder_id)
        self.assertIsNotNone(reminder)
        self.assertEqual(reminder[2], reminder_data["title"])  # title column
        
        # Get user reminders
        user_reminders = self.db_manager.get_user_reminders(user_id)
        self.assertTrue(len(user_reminders) > 0)
        
        # Update reminder
        new_title = "Updated Test Reminder"
        self.db_manager.update_reminder(reminder_id, title=new_title)
        
        updated_reminder = self.db_manager.get_reminder(reminder_id)
        self.assertEqual(updated_reminder[2], new_title)
        
        # Delete reminder
        self.db_manager.delete_reminder(reminder_id)
        deleted_reminder = self.db_manager.get_reminder(reminder_id)
        self.assertIsNone(deleted_reminder)
    
    def test_user_settings_operations(self):
        """Test user settings operations"""
        # First create a user
        user_id = 12345
        self.db_manager.create_user(user_id, "test_user", "Test User")
        
        # Set user setting
        self.db_manager.set_user_setting(user_id, "timezone", "EST")
        self.db_manager.set_user_setting(user_id, "notifications", "enabled")
        
        # Get user setting
        timezone = self.db_manager.get_user_setting(user_id, "timezone")
        self.assertEqual(timezone, "EST")
        
        notifications = self.db_manager.get_user_setting(user_id, "notifications")
        self.assertEqual(notifications, "enabled")
        
        # Get all user settings
        all_settings = self.db_manager.get_user_settings(user_id)
        self.assertIn("timezone", all_settings)
        self.assertIn("notifications", all_settings)
        self.assertEqual(all_settings["timezone"], "EST")
        self.assertEqual(all_settings["notifications"], "enabled")
        
        # Update user setting
        self.db_manager.set_user_setting(user_id, "timezone", "PST")
        updated_timezone = self.db_manager.get_user_setting(user_id, "timezone")
        self.assertEqual(updated_timezone, "PST")
    
    def test_google_credentials_operations(self):
        """Test Google credentials storage and retrieval"""
        # First create a user
        user_id = 12345
        self.db_manager.create_user(user_id, "test_user", "Test User")
        
        # Store credentials
        test_credentials = '{"token": "test_token", "refresh_token": "test_refresh"}'
        self.db_manager.store_google_credentials(user_id, test_credentials)
        
        # Retrieve credentials
        retrieved_credentials = self.db_manager.get_google_credentials(user_id)
        self.assertEqual(retrieved_credentials, test_credentials)
        
        # Update credentials
        updated_credentials = '{"token": "updated_token", "refresh_token": "updated_refresh"}'
        self.db_manager.store_google_credentials(user_id, updated_credentials)
        
        retrieved_updated = self.db_manager.get_google_credentials(user_id)
        self.assertEqual(retrieved_updated, updated_credentials)
    
    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Try to get non-existent user
        non_existent_user = self.db_manager.get_user(99999)
        self.assertIsNone(non_existent_user)
        
        # Try to get non-existent event
        non_existent_event = self.db_manager.get_event(99999)
        self.assertIsNone(non_existent_event)
        
        # Try to create reminder for non-existent user
        with self.assertRaises(Exception):
            self.db_manager.create_reminder(
                user_id=99999,
                title="Test",
                description="Test",
                reminder_time="2024-04-20 17:00:00"
            )
    
    def test_data_persistence(self):
        """Test that data persists across database connections"""
        # Create user
        user_id = 12345
        username = "persistent_user"
        self.db_manager.create_user(user_id, username, "Persistent User")
        
        # Close current connection and create new one
        self.db_manager.close()
        new_db_manager = DatabaseManager(db_path=self.test_db_path)
        
        # Check if user still exists
        user = new_db_manager.get_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)
        
        new_db_manager.close()

if __name__ == "__main__":
    unittest.main()

