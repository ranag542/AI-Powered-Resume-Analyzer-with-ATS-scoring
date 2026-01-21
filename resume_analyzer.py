import re
import os
import fitz  # PyMuPDF
from docx import Document
from typing import Dict, List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass

class ResumeAnalyzer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # Common skills database
        self.technical_skills = [
            'python', 'javascript', 'react', 'node.js', 'java', 'c++', 'c#',
            'sql', 'mongodb', 'aws', 'docker', 'kubernetes', 'git', 'github',
            'html', 'css', 'typescript', 'angular', 'vue.js', 'django', 'flask',
            'machine learning', 'data analysis', 'tableau', 'power bi',
            'rest api', 'graphql', 'firebase', 'postgresql', 'mysql',
            'react native', 'next.js', 'redux', 'jest', 'cypress', 'webpack'
        ]
        
        self.soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'critical thinking', 'time management', 'adaptability', 'creativity',
            'collaboration', 'project management', 'agile', 'scrum'
        ]
    
    def extract_and_clean_resume(self, filepath: str) -> Dict:
        """Extract text from file and clean it"""
        try:
            ext = filepath.split('.')[-1].lower()
            
            if ext == 'pdf':
                text = self._extract_from_pdf(filepath)
            elif ext in ['docx', 'doc']:
                text = self._extract_from_docx(filepath)
            elif ext == 'txt':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Analyze the text
            analysis = self.analyze_resume(cleaned_text)
            
            # Extract contact info
            contact_info = self._extract_contact_info(text)
            
            # Generate cleaning report
            cleaning_report = self._generate_cleaning_report(text, cleaned_text)
            
            # Validation
            validation = self._validate_resume(cleaned_text)
            
            # Word density analysis
            word_density = self._calculate_word_density(cleaned_text)
            
            return {
                'cleaned_text': cleaned_text,
                'cleaning_report': cleaning_report,
                'validation': validation,
                'contact_info': contact_info,
                'word_density': word_density,
                'original_text': text[:1000]  # Store first 1000 chars for reference
            }
            
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        return text
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove tables (pipe tables)
        text = re.sub(r'\|\s*[^|\n]+\s*\|', ' ', text)
        
        # Remove image references
        text = re.sub(r'\[(image|figure|graph|chart|picture)\]', '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '', text)
        
        # Remove unusual characters (keep basic punctuation)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n', text)
        
        return text.strip()
    
    def analyze_resume(self, text: str) -> Dict:
        """Analyze resume text"""
        # Basic metrics
        words = text.split()
        word_count = len(words)
        
        # Extract skills
        text_lower = text.lower()
        skills_found = []
        
        # Check for technical skills
        for skill in self.technical_skills:
            if skill in text_lower:
                skills_found.append(skill.title())
        
        # Check for soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                skills_found.append(skill.title())
        
        # Remove duplicates
        skills_found = list(set(skills_found))
        
        # Calculate readability (simplified)
        readability_score = self._calculate_readability(text)
        
        # Find quantifiable achievements
        quantifiable_achievements = self._find_quantifiable_achievements(text)
        
        # Count action verbs
        action_verbs_count = self._count_action_verbs(text)
        
        # Calculate skills match percentage
        all_skills = self.technical_skills + self.soft_skills
        found_skills_count = sum(1 for skill in all_skills if skill in text_lower)
        skills_match_percentage = round((found_skills_count / len(all_skills)) * 100, 1) if all_skills else 0
        
        # Get missing skills (top 10)
        found_skills_set = set(skill.lower() for skill in skills_found)
        all_skills_set = set(skill.lower() for skill in all_skills)
        missing_skills = [skill.title() for skill in list(all_skills_set - found_skills_set)[:10]]
        
        # Check sections
        has_summary = 'summary' in text_lower[:200] or 'objective' in text_lower[:200]
        has_education = 'education' in text_lower
        has_experience = any(term in text_lower for term in ['experience', 'work history', 'employment'])
        
        # Technical vs soft skills
        technical_skills = [s for s in skills_found if s.lower() in [ts.lower() for ts in self.technical_skills]]
        soft_skills = [s for s in skills_found if s.lower() in [ss.lower() for ss in self.soft_skills]]
        
        return {
            'word_count': word_count,
            'character_count': len(text),
            'skills_found': skills_found,
            'skills_count': len(skills_found),
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'readability_score': readability_score,
            'quantifiable_achievements': quantifiable_achievements,
            'action_verbs_count': action_verbs_count,
            'skills_match_percentage': skills_match_percentage,
            'missing_skills': missing_skills,
            'has_summary': has_summary,
            'has_education': has_education,
            'has_experience': has_experience
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate simplified readability score"""
        try:
            # Count sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 50.0
            
            # Count words
            words = text.split()
            if len(words) < 10:
                return 50.0
            
            # Simple Flesch score approximation
            avg_sentence_length = len(words) / len(sentences)
            
            # Simplified readability formula
            score = 100 - (avg_sentence_length * 1.0)
            return max(0, min(100, round(score, 1)))
        except:
            return 50.0
    
    def _find_quantifiable_achievements(self, text: str) -> List[str]:
        """Find quantifiable achievements"""
        patterns = [
            r'increased\s+[A-Za-z\s]+by\s+\d+%',
            r'reduced\s+[A-Za-z\s]+by\s+\d+%',
            r'improved\s+[A-Za-z\s]+by\s+\d+%',
            r'achieved\s+\d+%',
            r'saved\s+\$\d+',
            r'generated\s+\$\d+',
            r'managed\s+\$\d+\s+budget',
            r'led\s+\d+\s+team',
            r'trained\s+\d+\s+people',
        ]
        
        achievements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            achievements.extend(matches[:2])
        
        return achievements[:5]
    
    def _count_action_verbs(self, text: str) -> int:
        """Count action verbs"""
        action_verbs = [
            'achieved', 'managed', 'developed', 'led', 'implemented',
            'created', 'improved', 'increased', 'reduced', 'optimized',
            'designed', 'built', 'established', 'coordinated', 'trained',
            'mentored', 'supervised', 'initiated', 'spearheaded', 'delivered'
        ]
        
        count = 0
        text_lower = text.lower()
        for verb in action_verbs:
            count += text_lower.count(verb)
        
        return count
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = phones[0]
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact['linkedin'] = linkedin[0]
        
        # GitHub
        github_pattern = r'github\.com/[\w\-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact['github'] = github[0]
        
        return contact
    
    def _generate_cleaning_report(self, original_text: str, cleaned_text: str) -> Dict:
        """Generate cleaning report"""
        # Count tables (simple detection)
        table_matches = re.findall(r'\|\s*[^|\n]+\s*\|', original_text)
        
        # Count image references
        image_matches = re.findall(r'\[(image|figure|graph|chart|picture)\]', original_text, re.IGNORECASE)
        
        # Count unusual characters
        unusual_chars = re.findall(r'[^\x00-\x7F]', original_text)
        
        # Count headers/footers (simple detection)
        header_footer_patterns = [r'^\s*page\s*\d+\s*$', r'^\s*\d+\s*$']
        headers_footers = 0
        for line in original_text.split('\n'):
            for pattern in header_footer_patterns:
                if re.match(pattern, line.strip()):
                    headers_footers += 1
                    break
        
        original_length = len(original_text)
        final_length = len(cleaned_text)
        reduction_percentage = 0
        if original_length > 0:
            reduction_percentage = round(((original_length - final_length) / original_length) * 100, 2)
        
        return {
            'original_length': original_length,
            'final_length': final_length,
            'tables_removed': len(table_matches),
            'images_detected': len(image_matches),
            'unusual_chars_removed': len(unusual_chars),
            'headers_footers_removed': headers_footers,
            'reduction_percentage': reduction_percentage
        }
    
    def _validate_resume(self, text: str) -> Dict:
        """Validate resume against best practices"""
        word_count = len(text.split())
        
        validation = {
            'word_count': word_count,
            'validation_passed': True,
            'issues': []
        }
        
        # Check word count
        if word_count > 800:
            validation['issues'].append(f'Resume has {word_count} words (recommended: 500-800 max)')
            validation['validation_passed'] = False
        elif word_count < 300:
            validation['issues'].append(f'Resume has {word_count} words (recommended: at least 300)')
            validation['validation_passed'] = False
        
        # Check for tables
        if re.search(r'\|\s*[^|\n]+\s*\|', text):
            validation['issues'].append('Contains tables (may not parse well in ATS)')
            validation['validation_passed'] = False
        
        # Check for unusual characters
        unusual_chars = re.findall(r'[^\x00-\x7F]', text)
        if unusual_chars:
            validation['issues'].append(f'Contains {len(set(unusual_chars))} unusual characters')
        
        return validation
    
    def _calculate_word_density(self, text: str) -> Dict:
        """Calculate word frequency and density"""
        try:
            # Simple word extraction
            words = re.findall(r'\b\w+\b', text.lower())
            
            if not words:
                return {
                    'total_words': 0,
                    'unique_words': 0,
                    'top_keywords': [],
                    'keyword_density': {}
                }
            
            # Count frequency
            word_freq = Counter(words)
            
            # Remove stopwords and short words
            filtered_words = {word: freq for word, freq in word_freq.items() 
                             if word not in self.stop_words and len(word) > 2}
            
            # Get top keywords (max 20)
            top_keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # Calculate density
            total_words = len(words)
            keyword_density = {}
            for word, freq in top_keywords[:10]:
                if total_words > 0:
                    keyword_density[word] = round((freq / total_words) * 100, 2)
            
            return {
                'total_words': total_words,
                'unique_words': len(set(words)),
                'top_keywords': top_keywords,
                'keyword_density': keyword_density
            }
        except:
            return {
                'total_words': 0,
                'unique_words': 0,
                'top_keywords': [],
                'keyword_density': {}
            }