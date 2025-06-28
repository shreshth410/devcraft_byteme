"""
Unit tests for Poster Generator
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.poster_generator import PosterGenerator

class TestPosterGenerator(unittest.TestCase):
    """Test cases for Poster Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test posters
        self.test_dir = tempfile.mkdtemp()
        self.poster_generator = PosterGenerator(output_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_poster_generator_initialization(self):
        """Test poster generator initialization"""
        # Output directory should be created
        self.assertTrue(os.path.exists(self.test_dir))
        
        # Generator should have correct output directory
        self.assertEqual(self.poster_generator.output_dir, self.test_dir)
    
    def test_generate_event_poster(self):
        """Test event poster generation"""
        event_details = {
            "title": "Spring Festival",
            "date": "April 20, 2024",
            "time": "6:00 PM",
            "location": "Campus Quad",
            "description": "Join us for music, food, and fun!",
            "theme": "spring celebration",
            "colors": "green and yellow"
        }
        
        poster_path = self.poster_generator.generate_event_poster(event_details)
        
        # Should return a valid path
        self.assertIsNotNone(poster_path)
        self.assertTrue(isinstance(poster_path, str))
        
        # File should exist (as text placeholder)
        text_path = poster_path.replace('.png', '.txt')
        self.assertTrue(os.path.exists(text_path))
        
        # File should contain event information
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Spring Festival", content)
            self.assertIn("April 20, 2024", content)
            self.assertIn("Campus Quad", content)
    
    def test_generate_club_poster(self):
        """Test club poster generation"""
        additional_info = {
            "date": "March 15, 2024",
            "time": "7:00 PM",
            "location": "Student Center",
            "description": "Monthly club meeting with guest speaker"
        }
        
        poster_path = self.poster_generator.generate_club_poster(
            "Tech Club", "Meeting", additional_info
        )
        
        # Should return a valid path
        self.assertIsNotNone(poster_path)
        
        # File should exist (as text placeholder)
        text_path = poster_path.replace('.png', '.txt')
        self.assertTrue(os.path.exists(text_path))
        
        # File should contain club information
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Tech Club Meeting", content)
            self.assertIn("March 15, 2024", content)
    
    def test_generate_academic_poster(self):
        """Test academic poster generation"""
        course_info = {
            "title": "Computer Science Seminar",
            "date": "May 10, 2024",
            "time": "2:00 PM",
            "location": "CS Building Room 101",
            "description": "Advanced algorithms and data structures"
        }
        
        poster_path = self.poster_generator.generate_academic_poster(course_info)
        
        # Should return a valid path
        self.assertIsNotNone(poster_path)
        
        # File should exist (as text placeholder)
        text_path = poster_path.replace('.png', '.txt')
        self.assertTrue(os.path.exists(text_path))
        
        # File should contain academic information
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Computer Science Seminar", content)
            self.assertIn("academic professional", content)
    
    def test_list_generated_posters(self):
        """Test listing generated posters"""
        # Initially should be empty
        posters = self.poster_generator.list_generated_posters()
        self.assertEqual(len(posters), 0)
        
        # Generate a few posters
        event1 = {"title": "Event 1", "date": "2024-04-01"}
        event2 = {"title": "Event 2", "date": "2024-04-02"}
        
        self.poster_generator.generate_event_poster(event1)
        self.poster_generator.generate_event_poster(event2)
        
        # Should list generated posters
        posters = self.poster_generator.list_generated_posters()
        self.assertEqual(len(posters), 2)
        
        # Should be sorted by modification time (newest first)
        self.assertTrue(all(isinstance(path, str) for path in posters))
    
    def test_create_poster_prompt(self):
        """Test poster prompt creation"""
        prompt = self.poster_generator._create_poster_prompt(
            title="Test Event",
            date="2024-04-20",
            time="6:00 PM",
            location="Test Location",
            description="Test description",
            theme="modern",
            colors="blue and white"
        )
        
        # Should contain all required information
        self.assertIn("Test Event", prompt)
        self.assertIn("2024-04-20", prompt)
        self.assertIn("6:00 PM", prompt)
        self.assertIn("Test Location", prompt)
        self.assertIn("modern", prompt)
        self.assertIn("blue and white", prompt)
        
        # Should contain design specifications
        self.assertIn("DESIGN STYLE", prompt)
        self.assertIn("LAYOUT", prompt)
        self.assertIn("VISUAL ELEMENTS", prompt)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Empty event details
        result = self.poster_generator.generate_event_poster({})
        self.assertIsNotNone(result)  # Should still generate with defaults
        
        # Invalid output directory
        invalid_generator = PosterGenerator(output_dir="/invalid/path/that/does/not/exist")
        # Should handle gracefully (may create directory or fail gracefully)
        
        # None input
        result = self.poster_generator.generate_event_poster(None)
        # Should handle gracefully without crashing
    
    def test_filename_generation(self):
        """Test safe filename generation"""
        event_details = {
            "title": "Event with Special Characters!@#$%^&*()",
            "date": "2024-04-20"
        }
        
        poster_path = self.poster_generator.generate_event_poster(event_details)
        
        # Filename should be safe (no special characters)
        filename = os.path.basename(poster_path)
        self.assertNotIn("!", filename)
        self.assertNotIn("@", filename)
        self.assertNotIn("#", filename)
        
        # Should contain timestamp
        self.assertRegex(filename, r'\d{8}_\d{6}')
    
    def test_multiple_posters_same_event(self):
        """Test generating multiple posters for the same event"""
        event_details = {
            "title": "Same Event",
            "date": "2024-04-20"
        }
        
        # Generate multiple posters
        poster1 = self.poster_generator.generate_event_poster(event_details)
        poster2 = self.poster_generator.generate_event_poster(event_details)
        
        # Should generate different filenames (due to timestamp)
        self.assertNotEqual(poster1, poster2)
        
        # Both should exist
        text_path1 = poster1.replace('.png', '.txt')
        text_path2 = poster2.replace('.png', '.txt')
        self.assertTrue(os.path.exists(text_path1))
        self.assertTrue(os.path.exists(text_path2))

if __name__ == "__main__":
    unittest.main()

