from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
import traceback
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import analyzer classes
try:
    from resume_analyzer import ResumeAnalyzer
    from ats_scorer import ATSScorer
    ANALYZER_AVAILABLE = True
    print("✓ Resume analyzer imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import analyzer modules: {e}")
    print("⚠️ Running in demo mode with mock data")
    ANALYZER_AVAILABLE = False
    
    # Mock classes for testing
    class ResumeAnalyzer:
        def extract_and_clean_resume(self, filepath):
            return {
                'cleaned_text': 'Sample resume text for demonstration. This is a mock response when analyzer modules are not available.',
                'cleaning_report': {
                    'original_length': 1000,
                    'final_length': 950,
                    'tables_removed': 2,
                    'images_detected': 1,
                    'unusual_chars_removed': 5,
                    'headers_footers_removed': 3,
                    'reduction_percentage': 5.0
                },
                'validation': {
                    'word_count': 650,
                    'validation_passed': True,
                    'issues': []
                },
                'contact_info': {
                    'email': 'demo@example.com',
                    'phone': '(123) 456-7890'
                },
                'word_density': {
                    'total_words': 650,
                    'unique_words': 320,
                    'top_keywords': [('python', 15), ('development', 12), ('project', 10)],
                    'keyword_density': {'python': 2.3, 'development': 1.8}
                }
            }
        
        def analyze_resume(self, text):
            return {
                'word_count': 650,
                'character_count': 3500,
                'skills_found': ['Python', 'JavaScript', 'React', 'Communication', 'Teamwork'],
                'skills_count': 5,
                'technical_skills': ['Python', 'JavaScript', 'React'],
                'soft_skills': ['Communication', 'Teamwork'],
                'readability_score': 78.5,
                'quantifiable_achievements': ['Increased sales by 30%', 'Reduced costs by 20%'],
                'action_verbs_count': 12,
                'skills_match_percentage': 65.0,
                'missing_skills': ['AWS', 'Docker', 'Kubernetes'],
                'has_summary': True,
                'has_education': True,
                'has_experience': True
            }
    
    class ATSScorer:
        def calculate_score(self, resume_text, job_description=""):
            return {
                'ats_score': 78.5,
                'keyword_match_percentage': 65.0,
                'matched_keywords': ['python', 'javascript', 'react', 'development'],
                'missing_keywords': ['aws', 'docker', 'typescript', 'node.js'],
                'section_compliance': 85.0,
                'format_issues': []
            }

app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main HTML page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """API endpoint for resume analysis"""
    try:
        print("🔍 Analysis request received")
        
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        # Check if file is empty
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not allowed_file(resume_file.filename):
            return jsonify({
                'error': f'File type not allowed. Please upload: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        original_filename = secure_filename(resume_file.filename)
        filename = f"{uuid.uuid4()}_{original_filename}"
        filepath = os.path.join(upload_dir, filename)
        
        print(f"📁 Saving file: {original_filename} -> {filepath}")
        resume_file.save(filepath)
        
        # Initialize analyzers
        analyzer = ResumeAnalyzer()
        ats_scorer = ATSScorer()
        
        # Extract, clean, and analyze resume
        print("🔄 Extracting and cleaning resume...")
        extraction_result = analyzer.extract_and_clean_resume(filepath)
        cleaned_text = extraction_result['cleaned_text']
        
        # Analyze resume
        print("📊 Analyzing resume content...")
        analysis = analyzer.analyze_resume(cleaned_text)
        
        # Calculate ATS score against job description
        print("🎯 Calculating ATS score...")
        ats_results = ats_scorer.calculate_score(cleaned_text, job_description)
        
        # Calculate overall score
        overall_score = calculate_overall_score(analysis, ats_results, extraction_result.get('validation', {}))
        
        # Generate recommendations
        recommendations = generate_recommendations(analysis, ats_results, extraction_result)
        
        # Combine results
        results = {
            'resume_analysis': analysis,
            'ats_scoring': ats_results,
            'overall_score': overall_score,
            'recommendations': recommendations,
            'cleaning_report': extraction_result.get('cleaning_report', {}),
            'validation': extraction_result.get('validation', {}),
            'contact_info': extraction_result.get('contact_info', {}),
            'cleaned_text_preview': cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text,
            'word_density': extraction_result.get('word_density', {}),
            'demo_mode': not ANALYZER_AVAILABLE,
            'success': True
        }
        
        print(f"✅ Analysis complete. Overall score: {overall_score}")
        
        # Clean up file
        try:
            os.remove(filepath)
            print(f"🗑️ Cleaned up temporary file: {filepath}")
        except Exception as e:
            print(f"⚠️ Could not remove temporary file: {e}")
        
        return jsonify(results)
        
    except ValueError as e:
        print(f"❌ ValueError: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 400
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error. Please try again.',
            'details': str(e) if app.debug else None,
            'success': False
        }), 500

def calculate_overall_score(analysis, ats_results, validation):
    """Calculate weighted overall score"""
    try:
        weights = {
            'ats_score': 0.35,
            'keyword_match': 0.25,
            'skills_match': 0.15,
            'readability': 0.10,
            'validation': 0.15
        }
        
        # Validation score
        validation_score = 100
        if validation.get('issues'):
            validation_score = max(70, 100 - (len(validation['issues']) * 5))
        
        score = (
            (ats_results.get('ats_score', 0) * weights['ats_score']) +
            (ats_results.get('keyword_match_percentage', 0) * weights['keyword_match']) +
            (analysis.get('skills_match_percentage', 0) * weights['skills_match']) +
            (min(analysis.get('readability_score', 0) / 100, 1) * 100 * weights['readability']) +
            (validation_score * weights['validation'])
        )
        
        return round(min(score, 100), 1)
    except Exception as e:
        print(f"⚠️ Error calculating overall score: {e}")
        return 70.0

def generate_recommendations(analysis, ats_results, extraction_result):
    """Generate actionable recommendations"""
    recommendations = []
    
    # Word count recommendations
    word_count = analysis.get('word_count', 0)
    if word_count > 800:
        recommendations.append(f"Reduce word count from {word_count} to 500-800 words for better ATS compatibility")
    elif word_count < 300:
        recommendations.append(f"Increase word count from {word_count} to at least 300 words")
    
    # ATS score recommendations
    ats_score = ats_results.get('ats_score', 0)
    if ats_score < 70:
        recommendations.append("Improve ATS compatibility by using standard section headers and formatting")
    
    # Keyword recommendations
    keyword_match = ats_results.get('keyword_match_percentage', 0)
    if keyword_match < 60:
        recommendations.append("Add more relevant keywords from the job description")
        if ats_results.get('missing_keywords'):
            missing = ats_results['missing_keywords'][:3]
            recommendations.append(f"Consider adding keywords like: {', '.join(missing)}")
    
    # Skills recommendations
    if analysis.get('skills_count', 0) < 5:
        recommendations.append("Add more specific skills to your resume")
    
    # Readability recommendations
    readability = analysis.get('readability_score', 0)
    if readability < 60:
        recommendations.append("Improve readability by using shorter sentences and bullet points")
    
    # Cleaning recommendations
    cleaning_report = extraction_result.get('cleaning_report', {})
    if cleaning_report.get('tables_removed', 0) > 0:
        recommendations.append("Avoid using tables in your resume - ATS systems cannot parse them well")
    if cleaning_report.get('images_detected', 0) > 0:
        recommendations.append("Remove images and graphics - ATS cannot read text in images")
    
    # Add validation issues
    if extraction_result.get('validation', {}).get('issues'):
        recommendations.extend(extraction_result['validation']['issues'][:2])
    
    # Ensure we have at least some recommendations
    if not recommendations:
        recommendations.append("Your resume looks good! Consider customizing it for each job application.")
    
    return recommendations[:8]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-analyzer',
        'analyzer_available': ANALYZER_AVAILABLE,
        'success': True
    })

@app.route('/favicon.ico')
def favicon():
    """Return empty favicon to avoid 404 errors"""
    return '', 204

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    print("\n" + "="*50)
    print("🚀 Resume Analyzer Server Starting...")
    print("="*50)
    print(f"📁 Template directory: {os.path.join(os.getcwd(), 'templates')}")
    print(f"📁 Upload directory: {os.path.join(os.getcwd(), 'uploads')}")
    print(f"🔧 Analyzer available: {ANALYZER_AVAILABLE}")
    print("\n✅ Server is ready!")
    print("🌐 Open http://localhost:5000 in your browser")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')