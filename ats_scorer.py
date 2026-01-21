import re
from typing import Dict, List
from collections import Counter

class ATSScorer:
    def __init__(self):
        # Standard sections for ATS
        self.standard_sections = [
            'summary', 'objective', 'experience', 'work history',
            'education', 'skills', 'technical skills', 'certifications',
            'projects', 'awards', 'languages', 'references'
        ]
        
        # Common stopwords
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'])
    
    def calculate_score(self, resume_text: str, job_description: str = "") -> Dict:
        """Calculate ATS compatibility score"""
        results = {
            'ats_score': 0,
            'keyword_match_percentage': 0,
            'matched_keywords': [],
            'missing_keywords': [],
            'section_compliance': 0,
            'format_issues': [],
            'success': True
        }
        
        if not resume_text or not resume_text.strip():
            return results
        
        try:
            # 1. Keyword matching with job description
            if job_description and job_description.strip():
                keyword_results = self._analyze_keyword_match(resume_text, job_description)
                results.update(keyword_results)
            
            # 2. Section compliance check
            section_results = self._check_section_compliance(resume_text)
            results['section_compliance'] = section_results['compliance_score']
            results['format_issues'].extend(section_results['issues'])
            
            # 3. Format checks
            format_results = self._check_format_issues(resume_text)
            results['format_issues'].extend(format_results['issues'])
            
            # 4. Calculate overall ATS score
            results['ats_score'] = self._calculate_overall_ats_score(results)
            
        except Exception as e:
            print(f"Error in ATS scoring: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def _analyze_keyword_match(self, resume_text: str, job_description: str) -> Dict:
        """Analyze keyword match between resume and job description"""
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Extract keywords from resume
        resume_keywords = self._extract_keywords(resume_text)
        
        # Find matches
        job_keywords_set = set(job_keywords)
        resume_keywords_set = set(resume_keywords)
        
        matched_keywords = list(job_keywords_set.intersection(resume_keywords_set))
        missing_keywords = list(job_keywords_set - resume_keywords_set)
        
        # Calculate match percentage
        match_percentage = 0
        if job_keywords_set:
            match_percentage = round((len(matched_keywords) / len(job_keywords_set)) * 100, 1)
        
        return {
            'keyword_match_percentage': match_percentage,
            'matched_keywords': matched_keywords[:20],
            'missing_keywords': missing_keywords[:20]
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Simple tokenization
        tokens = re.findall(r'\b[a-z][a-z0-9]*\b', text.lower())
        
        # Remove stopwords and short words
        keywords = [token for token in tokens 
                   if token not in self.stop_words and len(token) > 2]
        
        # Count frequency and get most common
        if not keywords:
            return []
        
        word_freq = Counter(keywords)
        
        # Get most common keywords (appear at least twice or are longer words)
        common_keywords = []
        for word, freq in word_freq.most_common(50):
            if freq > 1 or len(word) > 5:
                common_keywords.append(word)
        
        return common_keywords[:30]
    
    def _check_section_compliance(self, resume_text: str) -> Dict:
        """Check if resume has standard section headers"""
        text_lower = resume_text.lower()
        sections_found = []
        
        for section in self.standard_sections:
            # Check for section headers (various formats)
            patterns = [
                f"\n{section}\n",
                f"\n{section}:",
                f"\n{section} ",
                f"^{section}\n",
                f"^{section}:",
                f"^{section} "
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.MULTILINE):
                    sections_found.append(section)
                    break
        
        # Calculate compliance score
        compliance_score = 0
        if self.standard_sections:
            compliance_score = round((len(sections_found) / min(len(self.standard_sections), 8)) * 100, 1)
        
        issues = []
        if compliance_score < 60:
            issues.append(f"Only {len(sections_found)} standard sections found (expected at least 5)")
        
        return {
            'sections_found': sections_found,
            'compliance_score': compliance_score,
            'issues': issues
        }
    
    def _check_format_issues(self, resume_text: str) -> Dict:
        """Check for common format issues"""
        issues = []
        
        # Check for tables
        if re.search(r'\|\s*[^|\n]+\s*\|', resume_text):
            issues.append("Contains tables (may not parse correctly in ATS)")
        
        # Check for images/graphics
        if re.search(r'\[(image|figure|graph|chart)\]', resume_text, re.IGNORECASE):
            issues.append("Contains image references (ATS cannot read images)")
        
        # Check length
        word_count = len(resume_text.split())
        if word_count > 1000:
            issues.append(f"Resume is long ({word_count} words). Consider shortening to 500-800 words")
        elif word_count < 200:
            issues.append(f"Resume is very short ({word_count} words). Add more details")
        
        # Check for unusual characters
        unusual_chars = re.findall(r'[^\x00-\x7F]', resume_text)
        if unusual_chars:
            issues.append(f"Contains {len(set(unusual_chars))} unusual characters")
        
        return {'issues': issues}
    
    def _calculate_overall_ats_score(self, results: Dict) -> float:
        """Calculate overall ATS score (0-100)"""
        try:
            scores = []
            
            # Keyword match weight: 40%
            scores.append(results.get('keyword_match_percentage', 0) * 0.4)
            
            # Section compliance weight: 30%
            scores.append(results.get('section_compliance', 0) * 0.3)
            
            # Format issues weight: 30% (inverse)
            format_penalty = 0
            if results.get('format_issues'):
                format_penalty = min(len(results['format_issues']) * 8, 30)
            scores.append((100 - format_penalty) * 0.3)
            
            # Calculate final score
            final_score = sum(scores)
            return round(min(max(final_score, 0), 100), 1)
        except:
            return 70.0