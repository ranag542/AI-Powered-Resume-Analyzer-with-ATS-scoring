"""
Resume Parser Module
Extracts text and structured information from PDF and DOCX resumes.
"""

import re
import PyPDF2
import docx
import pdfplumber
from typing import Dict, List, Optional


class ResumeParser:
    """Parse resumes from PDF and DOCX formats."""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}'
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return text.strip()
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file (PDF, DOCX, or TXT)."""
        file_ext = file_path.lower().split('.')[-1] if '.' in file_path else ''
        
        if file_ext == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == 'docx':
            return self.extract_text_from_docx(file_path)
        elif file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            raise ValueError(f"Unsupported file format: '.{file_ext}'. Only PDF, DOCX, and TXT are supported.")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text."""
        contact_info = {
            'email': None,
            'phone': None
        }
        
        # Extract email
        email_matches = re.findall(self.email_pattern, text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract phone
        phone_matches = re.findall(self.phone_pattern, text)
        if phone_matches:
            # Get first match and clean up
            phone = phone_matches[0].strip()
            contact_info['phone'] = phone
        
        return contact_info
    
    def extract_skills(self, text: str, skill_keywords: List[str]) -> List[str]:
        """Extract skills from resume text based on keyword list."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information from resume text."""
        education_keywords = [
            r'\b(B\.?S\.?|Bachelor|B\.?A\.?|B\.?Tech|B\.?E\.?)\b',
            r'\b(M\.?S\.?|Master|M\.?A\.?|M\.?Tech|M\.?B\.?A\.?|Ph\.?D\.?|Doctorate)\b',
            r'\bDiploma\b',
            r'\bAssociate\b'
        ]
        
        education = []
        lines = text.split('\n')
        
        for line in lines:
            for pattern in education_keywords:
                if re.search(pattern, line, re.IGNORECASE):
                    education.append(line.strip())
                    break
        
        return education
    
    def parse_resume(self, file_path: str, skill_keywords: Optional[List[str]] = None) -> Dict:
        """
        Parse resume and extract all relevant information.
        
        Args:
            file_path: Path to resume file (PDF or DOCX)
            skill_keywords: Optional list of skills to search for
            
        Returns:
            Dictionary containing parsed resume information
        """
        text = self.extract_text(file_path)
        contact_info = self.extract_contact_info(text)
        
        parsed_data = {
            'text': text,
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'education': self.extract_education(text),
        }
        
        if skill_keywords:
            parsed_data['skills'] = self.extract_skills(text, skill_keywords)
        
        return parsed_data
