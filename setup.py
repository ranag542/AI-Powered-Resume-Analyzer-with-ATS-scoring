"""Setup configuration for AI-Powered Resume Analyzer"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-resume-analyzer",
    version="1.0.0",
    author="Resume Analyzer Team",
    description="AI-Powered Resume Analyzer with ATS Scoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ranag542/AI-Powered-Resume-Analyzer-with-ATS-scoring",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "PyPDF2>=3.0.0",
        "python-docx>=1.0.0",
        "nltk>=3.8.0",
        "scikit-learn>=1.3.0",
        "pdfplumber>=0.10.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resume-analyzer=cli:main",
        ],
    },
)
