"""
Unit tests for ATS Scorer module
"""

import unittest
from ats_scorer import ATSScorer


class TestATSScorer(unittest.TestCase):
    """Test cases for ATSScorer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = ATSScorer()
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Python developer with experience in machine learning and data science"
        keywords = self.scorer.extract_keywords(text, top_n=5)
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
    
    def test_calculate_keyword_match_score_perfect_match(self):
        """Test keyword matching with perfect match."""
        resume_text = "Python Java JavaScript AWS Docker Kubernetes"
        job_desc = "Python Java JavaScript AWS Docker Kubernetes"
        
        score, details = self.scorer.calculate_keyword_match_score(resume_text, job_desc)
        
        self.assertGreater(score, 80)
        self.assertIsInstance(details, dict)
        self.assertIn('matched_keywords', details)
    
    def test_calculate_keyword_match_score_partial_match(self):
        """Test keyword matching with partial match."""
        resume_text = "Python Java experience in software development"
        job_desc = "Python JavaScript React Node.js required for frontend development"
        
        score, details = self.scorer.calculate_keyword_match_score(resume_text, job_desc)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIn('missing_keywords', details)
    
    def test_calculate_skills_score_all_matched(self):
        """Test skills scoring with all skills matched."""
        resume_skills = ['Python', 'Java', 'AWS']
        required_skills = ['Python', 'Java', 'AWS']
        
        score, details = self.scorer.calculate_skills_score(resume_skills, required_skills)
        
        self.assertEqual(score, 100.0)
        self.assertEqual(len(details['matched_skills']), 3)
        self.assertEqual(len(details['missing_skills']), 0)
    
    def test_calculate_skills_score_partial_match(self):
        """Test skills scoring with partial match."""
        resume_skills = ['Python', 'Java']
        required_skills = ['Python', 'Java', 'JavaScript', 'AWS']
        
        score, details = self.scorer.calculate_skills_score(resume_skills, required_skills)
        
        self.assertEqual(score, 50.0)
        self.assertEqual(len(details['matched_skills']), 2)
        self.assertEqual(len(details['missing_skills']), 2)
    
    def test_calculate_skills_score_case_insensitive(self):
        """Test that skills matching is case insensitive."""
        resume_skills = ['python', 'JAVA']
        required_skills = ['Python', 'Java']
        
        score, details = self.scorer.calculate_skills_score(resume_skills, required_skills)
        
        self.assertEqual(score, 100.0)
    
    def test_calculate_education_score_match(self):
        """Test education scoring with match."""
        resume_education = ['Bachelor of Science in Computer Science']
        required_education = ['Bachelor']
        
        score, details = self.scorer.calculate_education_score(resume_education, required_education)
        
        self.assertEqual(score, 100.0)
        self.assertTrue(details['found'])
    
    def test_calculate_education_score_no_match(self):
        """Test education scoring with no match."""
        resume_education = ['High School Diploma']
        required_education = ['Bachelor', 'Master']
        
        score, details = self.scorer.calculate_education_score(resume_education, required_education)
        
        self.assertLess(score, 100.0)
        self.assertFalse(details['found'])
    
    def test_calculate_format_score(self):
        """Test format scoring."""
        resume_text = """
        John Doe
        Email: john.doe@example.com
        Phone: 555-123-4567
        
        Experience:
        Software Engineer at Tech Corp
        
        Education:
        Bachelor of Science in Computer Science
        
        Skills:
        Python, Java, JavaScript
        """
        
        score, details = self.scorer.calculate_format_score(resume_text)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
        self.assertTrue(details['has_contact_info'])
        self.assertTrue(details['has_sections'])
    
    def test_calculate_ats_score_basic(self):
        """Test overall ATS score calculation."""
        resume_text = """
        John Doe
        john.doe@example.com
        
        Experience:
        Python developer with 5 years experience
        
        Skills: Python, Java, AWS
        """
        
        result = self.scorer.calculate_ats_score(resume_text=resume_text)
        
        self.assertIn('overall_score', result)
        self.assertIn('breakdown', result)
        self.assertIn('recommendations', result)
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
    
    def test_calculate_ats_score_with_job_description(self):
        """Test ATS score with job description."""
        resume_text = "Python developer with machine learning experience"
        job_description = "Looking for Python developer with ML and AI experience"
        
        result = self.scorer.calculate_ats_score(
            resume_text=resume_text,
            job_description=job_description
        )
        
        self.assertIn('keyword_match', result['breakdown'])
        self.assertGreater(result['overall_score'], 0)
    
    def test_calculate_ats_score_with_skills(self):
        """Test ATS score with skills."""
        resume_text = "Experienced in Python and Java"
        resume_skills = ['Python', 'Java']
        required_skills = ['Python', 'Java', 'JavaScript']
        
        result = self.scorer.calculate_ats_score(
            resume_text=resume_text,
            resume_skills=resume_skills,
            required_skills=required_skills
        )
        
        self.assertIn('skills_match', result['breakdown'])
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        resume_text = "Short resume"
        result = self.scorer.calculate_ats_score(resume_text=resume_text)
        
        self.assertIn('recommendations', result)
        self.assertIsInstance(result['recommendations'], list)
        self.assertGreater(len(result['recommendations']), 0)


if __name__ == '__main__':
    unittest.main()
