#!/usr/bin/env python3
"""
Demo script to showcase AI-Powered Resume Analyzer functionality
"""

import sys
from resume_parser import ResumeParser
from ats_scorer import ATSScorer


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_resume_analysis():
    """Demonstrate resume analysis functionality."""
    
    print_header("🤖 AI-Powered Resume Analyzer Demo")
    
    # Initialize components
    parser = ResumeParser()
    scorer = ATSScorer()
    
    # Sample resume text
    resume_text = """
    John Doe
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 5+ years of experience in Python, JavaScript,
    and cloud technologies. Expertise in building scalable web applications.
    
    TECHNICAL SKILLS
    - Programming: Python, JavaScript, Java, SQL
    - Frameworks: React, Django, Flask, Node.js
    - Cloud: AWS, Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2021 - Present
    - Developed microservices using Python and Docker
    - Led team of 5 engineers
    - Reduced application latency by 40%
    
    Software Engineer | StartupXYZ | 2019 - 2021
    - Built REST APIs using Django and Flask
    - Implemented CI/CD pipelines
    - Worked with AWS cloud services
    
    EDUCATION
    Master of Science in Computer Science
    Stanford University | 2017 - 2019
    
    Bachelor of Science in Computer Engineering
    UC Berkeley | 2013 - 2017
    """
    
    # Sample job description
    job_description = """
    Senior Software Engineer
    
    We're looking for an experienced software engineer with:
    - 5+ years of Python development
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Strong knowledge of microservices architecture
    - Expertise in React and modern frontend frameworks
    - Experience with Docker and Kubernetes
    - Bachelor's or Master's degree in Computer Science
    
    Required Skills:
    - Python, JavaScript, React
    - AWS, Docker, Kubernetes
    - SQL, NoSQL databases
    - CI/CD, Agile methodologies
    """
    
    print("📄 Analyzing Resume...")
    print("-" * 70)
    
    # Extract contact info
    contact_info = parser.extract_contact_info(resume_text)
    print(f"✅ Email: {contact_info['email']}")
    print(f"✅ Phone: {contact_info['phone']}")
    
    # Extract skills
    skill_keywords = ['Python', 'JavaScript', 'Java', 'React', 'Django', 
                      'Flask', 'AWS', 'Docker', 'Kubernetes', 'SQL']
    skills = parser.extract_skills(resume_text, skill_keywords)
    print(f"\n🎯 Skills Found ({len(skills)}):")
    for skill in sorted(skills):
        print(f"   • {skill}")
    
    # Extract education
    education = parser.extract_education(resume_text)
    print(f"\n🎓 Education ({len(education)} entries):")
    for edu in education:
        print(f"   • {edu}")
    
    # Calculate ATS score
    print_header("📊 ATS Score Calculation")
    
    required_skills = ['Python', 'JavaScript', 'React', 'AWS', 'Docker', 'Kubernetes']
    required_education = ['Bachelor', 'Master']
    
    ats_result = scorer.calculate_ats_score(
        resume_text=resume_text,
        job_description=job_description,
        resume_skills=skills,
        required_skills=required_skills,
        resume_education=education,
        required_education=required_education
    )
    
    # Display overall score
    overall_score = ats_result['overall_score']
    print(f"Overall ATS Score: {overall_score}%")
    
    if overall_score >= 80:
        print("Rating: ⭐ Excellent - Highly optimized for ATS")
    elif overall_score >= 60:
        print("Rating: ✓ Good - Should pass most ATS filters")
    else:
        print("Rating: ⚠ Needs Improvement - May not pass ATS screening")
    
    # Detailed breakdown
    print("\n" + "-" * 70)
    print("Score Breakdown:")
    print("-" * 70)
    
    breakdown = ats_result['breakdown']
    
    for category, data in breakdown.items():
        score = data['score']
        weight = data['weight']
        category_name = category.replace('_', ' ').title()
        print(f"\n{category_name}:")
        print(f"  Score: {score}% (Weight: {weight}%)")
        
        # Show details
        if category == 'keyword_match':
            details = data['details']
            matched = len(details.get('matched_keywords', []))
            missing = len(details.get('missing_keywords', []))
            print(f"  Matched: {matched} keywords")
            print(f"  Missing: {missing} keywords")
            if missing > 0:
                top_missing = details['missing_keywords'][:5]
                print(f"  Top Missing: {', '.join(top_missing)}")
        
        elif category == 'skills_match':
            details = data['details']
            matched = details.get('matched_skills', [])
            missing = details.get('missing_skills', [])
            if matched:
                print(f"  ✓ Matched: {', '.join(matched)}")
            if missing:
                print(f"  ✗ Missing: {', '.join(missing)}")
    
    # Recommendations
    print_header("💡 Recommendations")
    
    recommendations = ats_result.get('recommendations', [])
    for idx, recommendation in enumerate(recommendations, 1):
        print(f"{idx}. {recommendation}")
    
    print("\n" + "=" * 70)
    print("Demo Complete! ✨")
    print("=" * 70 + "\n")
    
    print("To try the full application:")
    print("  Web Interface:  streamlit run app.py")
    print("  CLI:            python cli.py your_resume.pdf")
    print()


if __name__ == "__main__":
    try:
        demo_resume_analysis()
    except Exception as e:
        print(f"Error during demo: {str(e)}", file=sys.stderr)
        sys.exit(1)
