#!/usr/bin/env python3
"""
Command-line interface for AI-Powered Resume Analyzer
"""

import argparse
import json
import sys
from pathlib import Path
from resume_parser import ResumeParser
from ats_scorer import ATSScorer


def print_section(title, char="="):
    """Print a formatted section header."""
    print(f"\n{char * 60}")
    print(f" {title}")
    print(f"{char * 60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Resume Analyzer with ATS Scoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a resume
  python cli.py resume.pdf
  
  # Analyze with job description
  python cli.py resume.pdf --job-description job.txt
  
  # Specify required skills
  python cli.py resume.pdf --skills "Python,Java,AWS"
  
  # Full analysis with all options
  python cli.py resume.pdf --job-description job.txt --skills "Python,Java" --education "Bachelor"
        """
    )
    
    parser.add_argument(
        'resume',
        type=str,
        help='Path to resume file (PDF or DOCX)'
    )
    
    parser.add_argument(
        '--job-description', '-j',
        type=str,
        help='Path to job description file or direct text'
    )
    
    parser.add_argument(
        '--skills', '-s',
        type=str,
        help='Comma-separated list of required skills'
    )
    
    parser.add_argument(
        '--education', '-e',
        type=str,
        help='Comma-separated list of required education levels'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for JSON results (optional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with full text'
    )
    
    args = parser.parse_args()
    
    # Validate resume file exists
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Error: Resume file not found: {args.resume}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize parsers
    resume_parser = ResumeParser()
    ats_scorer = ATSScorer()
    
    # Parse resume
    print_section("📄 Parsing Resume")
    print(f"File: {resume_path.name}")
    
    try:
        resume_text = resume_parser.extract_text(str(resume_path))
        contact_info = resume_parser.extract_contact_info(resume_text)
        
        # Default skills list
        default_skills = [
            "Python", "Java", "JavaScript", "C++", "SQL", "AWS", "Docker",
            "Machine Learning", "React", "Node.js", "Git", "Agile"
        ]
        resume_skills = resume_parser.extract_skills(resume_text, default_skills)
        resume_education = resume_parser.extract_education(resume_text)
        
        print("✅ Resume parsed successfully")
        print(f"   Email: {contact_info.get('email', 'Not found')}")
        print(f"   Phone: {contact_info.get('phone', 'Not found')}")
        print(f"   Skills found: {len(resume_skills)}")
        print(f"   Education entries: {len(resume_education)}")
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Load job description if provided
    job_description = ""
    if args.job_description:
        job_path = Path(args.job_description)
        if job_path.exists():
            with open(job_path, 'r', encoding='utf-8') as f:
                job_description = f.read()
            print(f"\n📋 Job description loaded from: {job_path.name}")
        else:
            job_description = args.job_description
            print(f"\n📋 Using provided job description text")
    
    # Parse required skills
    required_skills = None
    if args.skills:
        required_skills = [skill.strip() for skill in args.skills.split(',')]
        print(f"\n🎯 Required skills: {', '.join(required_skills)}")
    
    # Parse required education
    required_education = None
    if args.education:
        required_education = [edu.strip() for edu in args.education.split(',')]
        print(f"\n🎓 Required education: {', '.join(required_education)}")
    
    # Calculate ATS score
    print_section("🤖 Calculating ATS Score")
    
    ats_result = ats_scorer.calculate_ats_score(
        resume_text=resume_text,
        job_description=job_description,
        resume_skills=resume_skills if resume_skills else None,
        required_skills=required_skills,
        resume_education=resume_education if resume_education else None,
        required_education=required_education
    )
    
    # Display results
    print_section("📊 ATS Score Results", "=")
    
    overall_score = ats_result['overall_score']
    print(f"Overall ATS Score: {overall_score}% ", end="")
    
    if overall_score >= 80:
        print("⭐ Excellent")
    elif overall_score >= 60:
        print("✓ Good")
    else:
        print("⚠ Needs Improvement")
    
    print("\nScore Breakdown:")
    print("-" * 60)
    
    breakdown = ats_result['breakdown']
    
    for category, data in breakdown.items():
        score = data['score']
        weight = data['weight']
        print(f"\n{category.replace('_', ' ').title()}: {score}% (Weight: {weight}%)")
        
        # Print relevant details
        if category == 'format_score':
            details = data['details']
            print(f"  ✓ Contact Info: {'Yes' if details.get('has_contact_info') else 'No'}")
            print(f"  ✓ Clear Sections: {'Yes' if details.get('has_sections') else 'No'}")
            print(f"  ✓ Appropriate Length: {'Yes' if details.get('reasonable_length') else 'No'}")
        
        elif category == 'keyword_match':
            details = data['details']
            matched = len(details.get('matched_keywords', []))
            missing = len(details.get('missing_keywords', []))
            print(f"  Matched keywords: {matched}")
            print(f"  Missing keywords: {missing}")
        
        elif category == 'skills_match':
            details = data['details']
            matched = details.get('matched_skills', [])
            missing = details.get('missing_skills', [])
            if matched:
                print(f"  ✓ Matched: {', '.join(matched)}")
            if missing:
                print(f"  ✗ Missing: {', '.join(missing)}")
        
        elif category == 'education_match':
            details = data['details']
            if details.get('found'):
                print(f"  ✓ Education requirements met")
            else:
                print(f"  ✗ {details.get('note', 'Not found')}")
    
    # Recommendations
    print_section("💡 Recommendations")
    recommendations = ats_result.get('recommendations', [])
    for idx, recommendation in enumerate(recommendations, 1):
        print(f"{idx}. {recommendation}")
    
    # Verbose output
    if args.verbose:
        print_section("📝 Resume Content (First 500 characters)")
        print(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
    
    # Save to file if requested
    if args.output:
        output_data = {
            'resume_file': str(resume_path),
            'overall_score': overall_score,
            'breakdown': breakdown,
            'recommendations': recommendations,
            'contact_info': contact_info,
            'skills_found': resume_skills,
            'education_found': resume_education
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✅ Results saved to: {args.output}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if overall_score >= 60 else 1)


if __name__ == "__main__":
    main()
