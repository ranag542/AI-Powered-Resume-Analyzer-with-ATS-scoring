# 🤖 AI-Powered Resume Analyzer with ATS Scoring

An intelligent resume analysis tool that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). This tool analyzes resumes, compares them against job descriptions, and provides actionable recommendations to improve your chances of getting past ATS filters.

## ✨ Features

- **📄 Resume Parsing**: Extracts text from PDF and DOCX files
- **🎯 ATS Scoring**: Calculates compatibility score based on multiple factors
- **🔍 Keyword Analysis**: Matches resume keywords with job description
- **💡 Skills Detection**: Identifies technical and soft skills
- **🎓 Education Extraction**: Parses education information
- **📊 Detailed Reports**: Provides comprehensive breakdown of scores
- **💬 Smart Recommendations**: Offers actionable advice to improve your resume
- **🖥️ Dual Interface**: Web app (Streamlit) and command-line interface

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ranag542/AI-Powered-Resume-Analyzer-with-ATS-scoring.git
cd AI-Powered-Resume-Analyzer-with-ATS-scoring
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLTK data (will auto-download on first run):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Usage

#### Web Application (Streamlit)

Launch the interactive web interface:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Upload resume (PDF/DOCX)
- Optional: Add job description for tailored analysis
- Optional: Specify required skills and education
- View comprehensive ATS score and recommendations
- Interactive UI with detailed breakdowns

#### Command-Line Interface

Analyze a resume from the terminal:

```bash
# Basic analysis
python cli.py path/to/resume.pdf

# With job description
python cli.py resume.pdf --job-description job_description.txt

# With required skills
python cli.py resume.pdf --skills "Python,Java,AWS,Docker"

# With education requirements
python cli.py resume.pdf --education "Bachelor,Master"

# Full analysis with JSON output
python cli.py resume.pdf -j job.txt -s "Python,ML" -e "Bachelor" -o results.json

# Verbose output
python cli.py resume.pdf --verbose
```

## 📊 How It Works

### ATS Scoring Algorithm

The tool calculates an overall ATS score (0-100%) based on four weighted components:

1. **Format Score (20% weight)**
   - Contact information presence
   - Clear section structure
   - Appropriate length (100-2000 words)
   - Clean formatting (minimal special characters)

2. **Keyword Match (40% weight)**
   - Compares resume keywords with job description
   - Uses NLP to extract relevant terms
   - Identifies matched and missing keywords

3. **Skills Match (25% weight)**
   - Identifies technical and soft skills
   - Compares with required skills list
   - Highlights gaps in qualifications

4. **Education Match (15% weight)**
   - Extracts education information
   - Validates against requirements
   - Checks for degree levels (Bachelor's, Master's, PhD)

### Score Interpretation

- **80-100%**: ⭐ Excellent - Highly optimized for ATS
- **60-79%**: ✓ Good - Should pass most ATS filters
- **0-59%**: ⚠ Needs Improvement - May not pass ATS screening

## 🛠️ Technical Details

### Architecture

```
├── app.py              # Streamlit web application
├── cli.py              # Command-line interface
├── resume_parser.py    # Resume parsing logic
├── ats_scorer.py       # ATS scoring algorithm
└── requirements.txt    # Python dependencies
```

### Dependencies

- **Streamlit**: Web interface
- **PyPDF2 & pdfplumber**: PDF text extraction
- **python-docx**: DOCX file parsing
- **NLTK**: Natural language processing
- **scikit-learn**: Text analysis utilities

### Supported File Formats

- PDF (.pdf)
- Microsoft Word (.docx)

## 📝 Example Output

```
============================================================
 📊 ATS Score Results
============================================================

Overall ATS Score: 78% ✓ Good

Score Breakdown:
------------------------------------------------------------

Format Score: 100% (Weight: 20%)
  ✓ Contact Info: Yes
  ✓ Clear Sections: Yes
  ✓ Appropriate Length: Yes

Keyword Match: 72% (Weight: 40%)
  Matched keywords: 45
  Missing keywords: 18

Skills Match: 85% (Weight: 25%)
  ✓ Matched: Python, Java, AWS, Docker, Git
  ✗ Missing: Kubernetes

Education Match: 100% (Weight: 15%)
  ✓ Education requirements met

============================================================
 💡 Recommendations
============================================================

1. Include more relevant keywords: kubernetes, microservices, ci/cd
2. Great job! Your resume is well-optimized for ATS systems.
```

## 🎯 Best Practices

To get the best ATS score:

1. **Use Standard Headings**: Use common section titles like "Experience", "Education", "Skills"
2. **Include Keywords**: Match important keywords from the job description
3. **Clear Contact Info**: Always include email and phone number
4. **Optimize Length**: Keep resume between 1-2 pages (100-2000 words)
5. **Simple Formatting**: Avoid tables, images, and complex layouts
6. **Relevant Skills**: List skills that match the job requirements
7. **Quantify Achievements**: Use numbers and metrics where possible

## 🧪 Testing

Create a sample resume and job description to test the tool:

```bash
# Test with sample files
python cli.py sample_resume.pdf --job-description sample_job.txt --verbose
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and Streamlit
- Uses NLTK for natural language processing
- Inspired by real-world ATS systems used by recruiters

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This tool provides guidance for ATS optimization but does not guarantee job application success. Always tailor your resume to specific job requirements and company culture.