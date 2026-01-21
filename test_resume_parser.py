"""
Unit tests for Resume Parser module
"""

import unittest
import tempfile
import os
from resume_parser import ResumeParser


class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResumeParser()
        
    def test_extract_contact_info_with_email(self):
        """Test email extraction from text."""
        text = "Contact me at john.doe@example.com for more information."
        contact_info = self.parser.extract_contact_info(text)
        self.assertEqual(contact_info['email'], 'john.doe@example.com')
    
    def test_extract_contact_info_with_phone(self):
        """Test phone extraction from text."""
        text = "Call me at (555) 123-4567 or email."
        contact_info = self.parser.extract_contact_info(text)
        self.assertIsNotNone(contact_info['phone'])
        self.assertIn('555', contact_info['phone'])
    
    def test_extract_contact_info_no_email(self):
        """Test when no email is present."""
        text = "This is a resume without any email address."
        contact_info = self.parser.extract_contact_info(text)
        self.assertIsNone(contact_info['email'])
    
    def test_extract_skills(self):
        """Test skills extraction."""
        text = "I have experience with Python, Java, and JavaScript programming."
        skill_keywords = ['Python', 'Java', 'JavaScript', 'C++', 'Ruby']
        skills = self.parser.extract_skills(text, skill_keywords)
        
        self.assertIn('Python', skills)
        self.assertIn('Java', skills)
        self.assertIn('JavaScript', skills)
        self.assertNotIn('C++', skills)
    
    def test_extract_skills_case_insensitive(self):
        """Test skills extraction is case insensitive."""
        text = "Skilled in PYTHON and java"
        skill_keywords = ['Python', 'Java']
        skills = self.parser.extract_skills(text, skill_keywords)
        
        self.assertEqual(len(skills), 2)
    
    def test_extract_education(self):
        """Test education extraction."""
        text = """
        Education
        Bachelor of Science in Computer Science
        Master of Technology in AI
        """
        education = self.parser.extract_education(text)
        
        self.assertGreater(len(education), 0)
        self.assertTrue(any('Bachelor' in edu for edu in education))
    
    def test_extract_education_various_formats(self):
        """Test education extraction with various formats."""
        text = """
        B.S. in Computer Science
        M.Tech in Software Engineering
        Ph.D. in Machine Learning
        """
        education = self.parser.extract_education(text)
        
        self.assertGreaterEqual(len(education), 2)
    
    def test_unsupported_file_format(self):
        """Test that unsupported formats raise ValueError."""
        with self.assertRaises(ValueError):
            self.parser.extract_text("test.txt")


class TestResumeParserIntegration(unittest.TestCase):
    """Integration tests for resume parsing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResumeParser()
    
    def test_parse_resume_complete(self):
        """Test complete resume parsing workflow."""
        # This would require actual PDF/DOCX files for full testing
        # For now, we test the logic with text
        sample_text = """
        John Doe
        Email: john.doe@email.com
        Phone: (555) 123-4567
        
        Education:
        Bachelor of Science in Computer Science
        
        Skills:
        Python, Java, JavaScript, AWS, Docker
        
        Experience:
        Software Engineer at Tech Company
        """
        
        contact_info = self.parser.extract_contact_info(sample_text)
        self.assertEqual(contact_info['email'], 'john.doe@email.com')
        
        skills = self.parser.extract_skills(sample_text, ['Python', 'Java', 'AWS'])
        self.assertEqual(len(skills), 3)
        
        education = self.parser.extract_education(sample_text)
        self.assertGreater(len(education), 0)


if __name__ == '__main__':
    unittest.main()
