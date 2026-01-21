"""
ATS Scoring Module
Calculates Applicant Tracking System (ATS) compatibility score for resumes.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data (will be silent if already downloaded)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class ATSScorer:
    """Calculate ATS compatibility score for resumes."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def extract_keywords(self, text: str, top_n: int = 50) -> List[str]:
        """Extract top keywords from text."""
        # Tokenize and clean
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
        
        # Get most common words
        word_freq = Counter(words)
        keywords = [word for word, _ in word_freq.most_common(top_n)]
        
        return keywords
    
    def calculate_keyword_match_score(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """
        Calculate keyword match score between resume and job description.
        
        Returns:
            Tuple of (score, details_dict)
        """
        resume_keywords = set(self.extract_keywords(resume_text, top_n=100))
        job_keywords = set(self.extract_keywords(job_description, top_n=100))
        
        if not job_keywords:
            return 0.0, {'matched_keywords': [], 'missing_keywords': []}
        
        matched_keywords = resume_keywords.intersection(job_keywords)
        missing_keywords = job_keywords - resume_keywords
        
        # Calculate score as percentage of job keywords found in resume
        score = (len(matched_keywords) / len(job_keywords)) * 100
        
        details = {
            'matched_keywords': sorted(list(matched_keywords)),
            'missing_keywords': sorted(list(missing_keywords)),
            'match_percentage': round(score, 2)
        }
        
        return score, details
    
    def calculate_skills_score(self, resume_skills: List[str], required_skills: List[str]) -> Tuple[float, Dict]:
        """
        Calculate skills match score.
        
        Returns:
            Tuple of (score, details_dict)
        """
        if not required_skills:
            return 100.0, {'matched_skills': [], 'missing_skills': []}
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matched_skills = [skill for skill in required_skills if skill.lower() in resume_skills_lower]
        missing_skills = [skill for skill in required_skills if skill.lower() not in resume_skills_lower]
        
        score = (len(matched_skills) / len(required_skills)) * 100
        
        details = {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': round(score, 2)
        }
        
        return score, details
    
    def calculate_education_score(self, resume_education: List[str], required_education: List[str]) -> Tuple[float, Dict]:
        """
        Calculate education match score.
        
        Returns:
            Tuple of (score, details_dict)
        """
        if not required_education:
            return 100.0, {'found': True, 'details': 'No specific education requirement'}
        
        resume_education_text = ' '.join(resume_education).lower()
        
        # Check if any required education is mentioned
        found_education = []
        for edu in required_education:
            if edu.lower() in resume_education_text:
                found_education.append(edu)
        
        if found_education:
            score = 100.0
            details = {'found': True, 'matched_education': found_education}
        else:
            score = 50.0  # Partial score if education section exists but doesn't match
            if resume_education:
                details = {'found': False, 'note': 'Education section exists but does not match requirements'}
            else:
                score = 0.0
                details = {'found': False, 'note': 'No education information found'}
        
        return score, details
    
    def calculate_format_score(self, resume_text: str) -> Tuple[float, Dict]:
        """
        Calculate formatting score based on resume structure.
        
        Returns:
            Tuple of (score, details_dict)
        """
        score = 0
        details = {
            'has_contact_info': False,
            'has_sections': False,
            'reasonable_length': False,
            'no_special_chars': True
        }
        
        # Check for contact information (email pattern)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, resume_text):
            score += 25
            details['has_contact_info'] = True
        
        # Check for common resume sections
        sections = ['experience', 'education', 'skills', 'summary', 'work', 'employment']
        text_lower = resume_text.lower()
        if any(section in text_lower for section in sections):
            score += 25
            details['has_sections'] = True
        
        # Check for reasonable length (not too short, not too long)
        word_count = len(resume_text.split())
        if 100 < word_count < 2000:
            score += 25
            details['reasonable_length'] = True
        
        # Check for excessive special characters (might indicate parsing issues)
        special_char_ratio = len(re.findall(r'[^\w\s]', resume_text)) / max(len(resume_text), 1)
        if special_char_ratio < 0.1:
            score += 25
        else:
            details['no_special_chars'] = False
        
        return float(score), details
    
    def calculate_ats_score(
        self,
        resume_text: str,
        job_description: str = "",
        resume_skills: List[str] = None,
        required_skills: List[str] = None,
        resume_education: List[str] = None,
        required_education: List[str] = None
    ) -> Dict:
        """
        Calculate overall ATS score.
        
        Args:
            resume_text: Full text of the resume
            job_description: Job description text
            resume_skills: List of skills found in resume
            required_skills: List of required skills from job description
            resume_education: List of education found in resume
            required_education: List of required education
            
        Returns:
            Dictionary containing overall score and detailed breakdown
        """
        scores = {}
        weights = {}
        
        # Format score (always calculated)
        format_score, format_details = self.calculate_format_score(resume_text)
        scores['format'] = format_score
        weights['format'] = 20
        
        # Keyword match score
        if job_description:
            keyword_score, keyword_details = self.calculate_keyword_match_score(resume_text, job_description)
            scores['keyword_match'] = keyword_score
            weights['keyword_match'] = 40
        else:
            keyword_score, keyword_details = 0, {}
        
        # Skills score
        if resume_skills is not None and required_skills is not None:
            skills_score, skills_details = self.calculate_skills_score(resume_skills, required_skills)
            scores['skills'] = skills_score
            weights['skills'] = 25
        else:
            skills_score, skills_details = 0, {}
        
        # Education score
        if resume_education is not None and required_education is not None:
            education_score, education_details = self.calculate_education_score(resume_education, required_education)
            scores['education'] = education_score
            weights['education'] = 15
        else:
            education_score, education_details = 0, {}
        
        # Calculate weighted average
        total_weight = sum(weights.values())
        overall_score = sum(scores[key] * weights[key] for key in scores.keys()) / total_weight
        
        result = {
            'overall_score': round(overall_score, 2),
            'breakdown': {
                'format_score': {
                    'score': format_score,
                    'weight': weights['format'],
                    'details': format_details
                }
            }
        }
        
        if job_description:
            result['breakdown']['keyword_match'] = {
                'score': round(keyword_score, 2),
                'weight': weights['keyword_match'],
                'details': keyword_details
            }
        
        if resume_skills is not None and required_skills is not None:
            result['breakdown']['skills_match'] = {
                'score': round(skills_score, 2),
                'weight': weights['skills'],
                'details': skills_details
            }
        
        if resume_education is not None and required_education is not None:
            result['breakdown']['education_match'] = {
                'score': round(education_score, 2),
                'weight': weights['education'],
                'details': education_details
            }
        
        # Add recommendations
        result['recommendations'] = self._generate_recommendations(result['breakdown'])
        
        return result
    
    def _generate_recommendations(self, breakdown: Dict) -> List[str]:
        """Generate recommendations based on scoring breakdown."""
        recommendations = []
        
        # Format recommendations
        if 'format_score' in breakdown and breakdown['format_score']['score'] < 80:
            details = breakdown['format_score']['details']
            if not details.get('has_contact_info'):
                recommendations.append("Add clear contact information (email, phone)")
            if not details.get('has_sections'):
                recommendations.append("Organize resume with clear sections (Experience, Education, Skills)")
            if not details.get('reasonable_length'):
                recommendations.append("Adjust resume length to 100-2000 words for optimal readability")
        
        # Keyword recommendations
        if 'keyword_match' in breakdown and breakdown['keyword_match']['score'] < 60:
            missing = breakdown['keyword_match']['details'].get('missing_keywords', [])
            if missing:
                top_missing = missing[:5]
                recommendations.append(f"Include more relevant keywords: {', '.join(top_missing)}")
        
        # Skills recommendations
        if 'skills_match' in breakdown and breakdown['skills_match']['score'] < 70:
            missing = breakdown['skills_match']['details'].get('missing_skills', [])
            if missing:
                recommendations.append(f"Add missing required skills: {', '.join(missing)}")
        
        # Education recommendations
        if 'education_match' in breakdown and not breakdown['education_match']['details'].get('found'):
            recommendations.append("Ensure education section is clearly visible and matches job requirements")
        
        if not recommendations:
            recommendations.append("Great job! Your resume is well-optimized for ATS systems.")
        
        return recommendations
