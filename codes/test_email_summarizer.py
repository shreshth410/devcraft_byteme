"""
Unit tests for Email Summarizer
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.email_summarizer import EmailSummarizer

class TestEmailSummarizer(unittest.TestCase):
    """Test cases for Email Summarizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_summarizer = EmailSummarizer()
    
    def test_email_summarizer_initialization(self):
        """Test email summarizer initialization"""
        self.assertIsNotNone(self.email_summarizer)
        self.assertEqual(self.email_summarizer.max_summary_length, 200)
        self.assertTrue(len(self.email_summarizer.key_sections) > 0)
    
    def test_summarize_email_basic(self):
        """Test basic email summarization"""
        email_content = """
        Dear students,
        
        This is to inform you about the upcoming midterm examinations scheduled for next week.
        Please note that all exams will be held in the main examination hall from 9 AM to 12 PM.
        Students are required to bring their student ID cards and writing materials.
        Late arrivals will not be permitted.
        
        For any queries, contact the academic office.
        
        Best regards,
        Academic Office
        """
        
        result = self.email_summarizer.summarize_email(
            email_content,
            sender="Academic Office",
            subject="Midterm Examination Notice"
        )
        
        # Should contain required fields
        self.assertIn("summary", result)
        self.assertIn("key_points", result)
        self.assertIn("action_items", result)
        self.assertIn("important_dates", result)
        self.assertIn("priority", result)
        self.assertIn("sender", result)
        self.assertIn("subject", result)
        
        # Should have correct metadata
        self.assertEqual(result["sender"], "Academic Office")
        self.assertEqual(result["subject"], "Midterm Examination Notice")
        self.assertIn(result["priority"], ["High", "Medium", "Low"])
        
        # Summary should not be empty
        self.assertTrue(len(result["summary"]) > 0)
    
    def test_summarize_notice_basic(self):
        """Test basic notice summarization"""
        notice_content = """
        NOTICE: New Library Hours
        
        Effective immediately, the library will be open from 8 AM to 10 PM on weekdays
        and 10 AM to 6 PM on weekends. This change is due to increased student demand
        for extended study hours during the examination period.
        
        All students and faculty are requested to take note of these new timings.
        The library staff will be available during these hours to assist with any queries.
        
        This policy will remain in effect until further notice.
        """
        
        result = self.email_summarizer.summarize_notice(
            notice_content,
            title="New Library Hours"
        )
        
        # Should contain required fields
        self.assertIn("summary", result)
        self.assertIn("key_points", result)
        self.assertIn("important_dates", result)
        self.assertIn("affected_groups", result)
        self.assertIn("urgency", result)
        self.assertIn("title", result)
        
        # Should have correct metadata
        self.assertEqual(result["title"], "New Library Hours")
        self.assertIn(result["urgency"], ["Urgent", "Moderate", "Low"])
        
        # Should identify affected groups
        self.assertTrue(len(result["affected_groups"]) > 0)
    
    def test_priority_detection(self):
        """Test priority detection in emails"""
        # High priority email
        urgent_email = """
        URGENT: System maintenance tonight
        
        This is an urgent notice about emergency system maintenance.
        All services will be unavailable from 11 PM to 3 AM.
        Immediate action required from all users.
        """
        
        result = self.email_summarizer.summarize_email(urgent_email, subject="URGENT: System Maintenance")
        self.assertEqual(result["priority"], "High")
        
        # Medium priority email
        reminder_email = """
        Reminder: Assignment submission deadline
        
        This is a friendly reminder that your assignment is due next week.
        Please ensure you submit it on time.
        """
        
        result = self.email_summarizer.summarize_email(reminder_email, subject="Reminder: Assignment Due")
        self.assertEqual(result["priority"], "Medium")
        
        # Low priority email
        info_email = """
        Information about upcoming events
        
        Here are some events happening on campus this month.
        Feel free to attend any that interest you.
        """
        
        result = self.email_summarizer.summarize_email(info_email, subject="Campus Events")
        self.assertEqual(result["priority"], "Low")
    
    def test_urgency_detection(self):
        """Test urgency detection in notices"""
        # Urgent notice
        urgent_notice = """
        EMERGENCY: Campus closure due to weather
        
        Due to severe weather conditions, the campus will be closed immediately.
        All classes and activities are cancelled for today.
        """
        
        result = self.email_summarizer.summarize_notice(urgent_notice, title="Emergency Campus Closure")
        self.assertEqual(result["urgency"], "Urgent")
        
        # Moderate urgency notice
        deadline_notice = """
        Important: Registration deadline approaching
        
        The deadline for course registration is next Friday.
        Please complete your registration before the deadline.
        """
        
        result = self.email_summarizer.summarize_notice(deadline_notice, title="Registration Deadline")
        self.assertEqual(result["urgency"], "Moderate")
    
    def test_action_items_extraction(self):
        """Test extraction of action items"""
        email_with_actions = """
        Dear students,
        
        Please submit your assignments by Friday.
        You must register for the exam by tomorrow.
        Students need to bring their ID cards.
        Complete the online survey before the deadline.
        """
        
        result = self.email_summarizer.summarize_email(email_with_actions)
        action_items = result["action_items"]
        
        # Should find action items
        self.assertTrue(len(action_items) > 0)
        
        # Should contain action-oriented text
        action_text = " ".join(action_items).lower()
        self.assertTrue(any(word in action_text for word in ["submit", "register", "bring", "complete"]))
    
    def test_date_extraction(self):
        """Test extraction of dates and deadlines"""
        email_with_dates = """
        Important dates to remember:
        - Assignment due: March 15, 2024
        - Exam date: 04/20/2024
        - Meeting on Monday, April 22
        - Deadline: 12/31/2023
        """
        
        result = self.email_summarizer.summarize_email(email_with_dates)
        dates = result["important_dates"]
        
        # Should find some dates
        self.assertTrue(len(dates) > 0)
    
    def test_affected_groups_extraction(self):
        """Test extraction of affected groups from notices"""
        notice_with_groups = """
        This notice applies to all undergraduate students and faculty members.
        Graduate students are also affected by this policy change.
        The administration and staff should take note of these updates.
        """
        
        result = self.email_summarizer.summarize_notice(notice_with_groups)
        affected_groups = result["affected_groups"]
        
        # Should identify groups
        self.assertTrue(len(affected_groups) > 0)
        
        # Should contain expected groups
        groups_text = " ".join(affected_groups).lower()
        self.assertTrue(any(group in groups_text for group in ["students", "faculty", "staff"]))
    
    def test_clean_email_content(self):
        """Test email content cleaning"""
        dirty_email = """
        From: sender@example.com
        To: recipient@example.com
        Subject: Test Email
        Date: 2024-04-20
        
        This is the actual email content.
        It should be preserved after cleaning.
        
        --
        Best regards,
        Sender Name
        Email: sender@example.com
        """
        
        cleaned = self.email_summarizer._clean_email_content(dirty_email)
        
        # Should remove headers
        self.assertNotIn("From:", cleaned)
        self.assertNotIn("To:", cleaned)
        self.assertNotIn("Subject:", cleaned)
        
        # Should preserve main content
        self.assertIn("actual email content", cleaned)
        
        # Should remove signature
        self.assertNotIn("Best regards", cleaned)
    
    def test_format_summary_for_telegram(self):
        """Test formatting summary for Telegram"""
        summary_data = {
            "summary": "Test summary",
            "subject": "Test Subject",
            "sender": "Test Sender",
            "priority": "High",
            "key_points": ["Point 1", "Point 2"],
            "action_items": ["Action 1", "Action 2"],
            "important_dates": ["2024-04-20", "2024-04-21"]
        }
        
        formatted = self.email_summarizer.format_summary_for_telegram(summary_data)
        
        # Should contain all sections
        self.assertIn("Email Summary", formatted)
        self.assertIn("Subject:", formatted)
        self.assertIn("From:", formatted)
        self.assertIn("Priority:", formatted)
        self.assertIn("Summary:", formatted)
        self.assertIn("Key Points:", formatted)
        self.assertIn("Action Items:", formatted)
        self.assertIn("Important Dates:", formatted)
        
        # Should contain the actual data
        self.assertIn("Test summary", formatted)
        self.assertIn("Test Subject", formatted)
        self.assertIn("High", formatted)
    
    def test_empty_content_handling(self):
        """Test handling of empty or minimal content"""
        # Empty content
        result = self.email_summarizer.summarize_email("")
        self.assertIn("summary", result)
        
        # Very short content
        result = self.email_summarizer.summarize_email("Hi")
        self.assertIn("summary", result)
        
        # None content should be handled gracefully
        try:
            result = self.email_summarizer.summarize_email(None)
            # Should not crash
        except:
            pass  # Expected to handle gracefully
    
    def test_very_long_content(self):
        """Test handling of very long content"""
        long_content = "This is a very long email content. " * 1000
        
        result = self.email_summarizer.summarize_email(long_content)
        
        # Should still produce a summary
        self.assertIn("summary", result)
        self.assertTrue(len(result["summary"]) > 0)
        
        # Summary should be reasonable length
        summary_words = len(result["summary"].split())
        self.assertLessEqual(summary_words, self.email_summarizer.max_summary_length * 2)

if __name__ == "__main__":
    unittest.main()

