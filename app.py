"""
AI-Powered Resume Analyzer with ATS Scoring
Streamlit Web Application
"""

import streamlit as st
import tempfile
import os
from resume_parser import ResumeParser
from ats_scorer import ATSScorer


# Common technical skills for reference
DEFAULT_SKILLS = [
    "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Swift",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Git", "Agile", "Scrum", "CI/CD",
    "HTML", "CSS", "REST API", "GraphQL",
    "TensorFlow", "PyTorch", "scikit-learn",
    "Leadership", "Communication", "Problem Solving", "Teamwork"
]


def main():
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🤖 AI-Powered Resume Analyzer with ATS Scoring")
    st.markdown("""
    Upload your resume and optionally provide a job description to get:
    - **ATS Compatibility Score** - How well your resume matches Applicant Tracking Systems
    - **Keyword Analysis** - Match between your resume and job requirements
    - **Skills Assessment** - Identified skills and gaps
    - **Actionable Recommendations** - Improve your resume's effectiveness
    """)
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Initialize parsers
    parser = ResumeParser()
    scorer = ATSScorer()
    
    # File upload
    st.header("📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Parse resume
            with st.spinner("Parsing resume..."):
                resume_text = parser.extract_text(tmp_file_path)
                contact_info = parser.extract_contact_info(resume_text)
                resume_skills = parser.extract_skills(resume_text, DEFAULT_SKILLS)
                resume_education = parser.extract_education(resume_text)
            
            # Display parsed information
            st.success("✅ Resume parsed successfully!")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 ATS Score", "📝 Resume Preview", "🎯 Skills", "📧 Contact Info"])
            
            with tab2:
                st.subheader("Resume Content")
                with st.expander("View Full Resume Text", expanded=False):
                    st.text_area("Resume Text", resume_text, height=300, disabled=True)
            
            with tab3:
                st.subheader("Identified Skills")
                if resume_skills:
                    # Display skills in columns
                    cols = st.columns(3)
                    for idx, skill in enumerate(sorted(resume_skills)):
                        cols[idx % 3].markdown(f"✅ {skill}")
                else:
                    st.info("No skills from the default list were found. This might affect your ATS score.")
            
            with tab4:
                st.subheader("Contact Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Email", contact_info.get('email', 'Not found'))
                with col2:
                    st.metric("Phone", contact_info.get('phone', 'Not found'))
                
                if resume_education:
                    st.subheader("Education")
                    for edu in resume_education:
                        st.write(f"🎓 {edu}")
            
            # Job description section
            st.header("💼 Job Description (Optional)")
            job_description = st.text_area(
                "Paste the job description here to get a tailored ATS score",
                height=200,
                help="Add the job description to compare your resume against specific requirements"
            )
            
            # Required skills (optional)
            st.subheader("Required Skills (Optional)")
            required_skills_input = st.text_area(
                "Enter required skills (one per line or comma-separated)",
                help="List the skills required for the job"
            )
            
            required_skills = []
            if required_skills_input:
                # Split by newlines or commas
                required_skills = [
                    skill.strip() 
                    for skill in required_skills_input.replace(',', '\n').split('\n') 
                    if skill.strip()
                ]
            
            # Required education (optional)
            st.subheader("Required Education (Optional)")
            required_education_input = st.text_input(
                "Enter required education (e.g., Bachelor, Master, PhD)",
                help="Specify the education level required"
            )
            
            required_education = []
            if required_education_input:
                required_education = [
                    edu.strip() 
                    for edu in required_education_input.split(',') 
                    if edu.strip()
                ]
            
            # Calculate ATS Score
            if st.button("🚀 Calculate ATS Score", type="primary"):
                with st.spinner("Calculating ATS score..."):
                    ats_result = scorer.calculate_ats_score(
                        resume_text=resume_text,
                        job_description=job_description if job_description else "",
                        resume_skills=resume_skills if resume_skills else None,
                        required_skills=required_skills if required_skills else None,
                        resume_education=resume_education if resume_education else None,
                        required_education=required_education if required_education else None
                    )
                
                # Display results in the ATS Score tab
                with tab1:
                    # Overall score with color coding
                    overall_score = ats_result['overall_score']
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        # Color based on score - validate color for security
                        if overall_score >= 80:
                            color = "#28a745"  # green
                            rating = "Excellent"
                        elif overall_score >= 60:
                            color = "#ff8c00"  # orange
                            rating = "Good"
                        else:
                            color = "#dc3545"  # red
                            rating = "Needs Improvement"
                        
                        st.markdown(f"""
                        <div style='padding: 20px; background-color: {color}; border-radius: 10px; text-align: center;'>
                            <h1 style='color: white; margin: 0;'>{overall_score}%</h1>
                            <p style='color: white; margin: 0;'>Overall ATS Score</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Rating", rating)
                    
                    with col3:
                        st.metric("Status", "✅ Pass" if overall_score >= 60 else "❌ Review")
                    
                    st.divider()
                    
                    # Detailed breakdown
                    st.subheader("📊 Score Breakdown")
                    
                    breakdown = ats_result['breakdown']
                    
                    # Format score
                    if 'format_score' in breakdown:
                        with st.expander("📄 Format Score", expanded=True):
                            score_data = breakdown['format_score']
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Score", f"{score_data['score']}%", 
                                         delta=f"Weight: {score_data['weight']}%")
                            with col2:
                                details = score_data['details']
                                st.write("**Checklist:**")
                                st.write(f"{'✅' if details.get('has_contact_info') else '❌'} Contact Information")
                                st.write(f"{'✅' if details.get('has_sections') else '❌'} Clear Sections")
                                st.write(f"{'✅' if details.get('reasonable_length') else '❌'} Appropriate Length")
                                st.write(f"{'✅' if details.get('no_special_chars') else '❌'} Clean Formatting")
                    
                    # Keyword match
                    if 'keyword_match' in breakdown:
                        with st.expander("🔑 Keyword Match", expanded=True):
                            score_data = breakdown['keyword_match']
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Score", f"{score_data['score']}%",
                                         delta=f"Weight: {score_data['weight']}%")
                            with col2:
                                details = score_data['details']
                                st.write(f"**Matched Keywords:** {len(details.get('matched_keywords', []))}")
                                st.write(f"**Missing Keywords:** {len(details.get('missing_keywords', []))}")
                                
                                if details.get('matched_keywords'):
                                    with st.expander("View Matched Keywords"):
                                        st.write(", ".join(details['matched_keywords'][:20]))
                                
                                if details.get('missing_keywords'):
                                    with st.expander("View Missing Keywords"):
                                        st.write(", ".join(details['missing_keywords'][:20]))
                    
                    # Skills match
                    if 'skills_match' in breakdown:
                        with st.expander("💡 Skills Match", expanded=True):
                            score_data = breakdown['skills_match']
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Score", f"{score_data['score']}%",
                                         delta=f"Weight: {score_data['weight']}%")
                            with col2:
                                details = score_data['details']
                                if details.get('matched_skills'):
                                    st.write("**Matched Skills:**")
                                    st.write(", ".join(details['matched_skills']))
                                
                                if details.get('missing_skills'):
                                    st.write("**Missing Required Skills:**")
                                    st.warning(", ".join(details['missing_skills']))
                    
                    # Education match
                    if 'education_match' in breakdown:
                        with st.expander("🎓 Education Match", expanded=True):
                            score_data = breakdown['education_match']
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Score", f"{score_data['score']}%",
                                         delta=f"Weight: {score_data['weight']}%")
                            with col2:
                                details = score_data['details']
                                if details.get('found'):
                                    st.success("✅ Education requirements met")
                                    if 'matched_education' in details:
                                        st.write(", ".join(details['matched_education']))
                                else:
                                    st.warning(details.get('note', 'Education information not found'))
                    
                    st.divider()
                    
                    # Recommendations
                    st.subheader("💡 Recommendations")
                    recommendations = ats_result.get('recommendations', [])
                    for idx, recommendation in enumerate(recommendations, 1):
                        st.info(f"{idx}. {recommendation}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### About
    This AI-powered tool analyzes resumes and calculates ATS (Applicant Tracking System) compatibility scores.
    
    **Features:**
    - Resume parsing (PDF/DOCX)
    - Keyword matching
    - Skills analysis
    - ATS scoring
    - Personalized recommendations
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** For best results, provide both a resume and job description.")


if __name__ == "__main__":
    main()
