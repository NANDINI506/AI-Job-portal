# 🚀 AI-Powered Job Portal & Resume Builder

A comprehensive, intelligent job portal system with AI-powered resume building, job matching, and automated job scraping capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [AI Components](#ai-components)
- [Job Scraping](#job-scraping)
- [Resume Builder](#resume-builder)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This is a full-stack job portal application built with **FastAPI** and **Python**, featuring:

- **AI-Powered Job Matching**: Intelligent skill-based job recommendations
- **Automated Job Scraping**: Real-time job data from multiple sources
- **Smart Resume Builder**: AI-enhanced resume creation and optimization
- **ATS Optimization**: Resume scoring and improvement suggestions
- **User Management**: Complete user authentication and profile system
- **Email Notifications**: Automated job alerts and updates

## ✨ Key Features

### 🔍 **Smart Job Search & Matching**

- **Intelligent Job Matching**: AI-powered skill matching algorithm
- **Real-time Scraping**: Automated job collection from Adzuna API
- **Duplicate Prevention**: Advanced duplicate detection and filtering
- **Location-based Search**: Geographic job filtering and recommendations
- **Skill-based Filtering**: Intelligent job categorization and matching

### 📝 **AI Resume Builder**

- **Gemini AI Integration**: Advanced AI-powered resume generation
- **ATS Optimization**: Resume scoring and improvement suggestions
- **Multiple Formats**: PDF generation with professional templates
- **Skill Extraction**: Automatic skill identification from text
- **Customizable Templates**: Professional resume layouts

### 🎯 **ATS (Applicant Tracking System)**

- **Resume Scoring**: Comprehensive ATS compatibility scoring
- **Keyword Analysis**: Job description keyword matching
- **Improvement Suggestions**: Actionable recommendations for better scores
- **Format Validation**: ATS-friendly formatting checks

### 📧 **Smart Notifications**

- **Email Alerts**: Automated job matching notifications
- **In-app Notifications**: Real-time updates and alerts
- **Duplicate Prevention**: Smart notification deduplication
- **Personalized Content**: User-specific job recommendations

### 👥 **User Management**

- **Authentication System**: Secure login and registration
- **Profile Management**: Comprehensive user profiles
- **Skill Tracking**: User skill management and updates
- **Application History**: Complete job application tracking

## 🏗️ Architecture

### **Technology Stack**

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Google Gemini AI, NLTK, spaCy
- **Frontend**: HTML Templates with Bootstrap
- **Email**: SMTP with Gmail integration
- **Scheduling**: APScheduler for automated tasks

### **Project Structure**

```
job-portal/
├── app/                          # Main application code
│   ├── main.py                  # FastAPI application & routes
│   ├── models.py                # Database models
│   ├── database.py              # Database configuration
│   ├── auth.py                  # Authentication utilities
│   ├── scraper.py               # Job scraping engine
│   ├── nlp_utils.py             # NLP and AI utilities
│   ├── ats_utils.py             # ATS scoring system
│   ├── email_utils.py           # Email functionality
│   ├── job_description_processor.py  # Job description processing
│   ├── analysis.py              # Data analysis utilities
│   ├── templates/               # HTML templates
│   ├── static/                  # Static assets
│   ├── data/                    # Data files (skills taxonomy)
│   └── resume_builder/          # Resume building system
│       ├── gemini_integration.py # AI integration
│       ├── models.py            # Resume models
│       └── pdf_generator.py     # PDF generation
├── resumes/                     # User resume storage
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🚀 Installation

### **Prerequisites**

- Python 3.8 or higher
- pip package manager
- Git

### **Step 1: Clone the Repository**

```bash
git clone <repository-url>
cd job-portal
```

### **Step 2: Create Virtual Environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 4: Environment Configuration**

Create a `.env` file in the root directory:

```env
# Email Configuration
EMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Database Configuration
DATABASE_URL=sqlite:///./jobs.db
```

### **Step 5: Initialize Database**

```bash
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

### **Step 6: Run the Application**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ⚙️ Configuration

### **Environment Variables**

| Variable             | Description                      | Required | Default               |
| -------------------- | -------------------------------- | -------- | --------------------- |
| `EMAIL_SENDER`       | Gmail address for sending emails | Yes      | -                     |
| `GMAIL_APP_PASSWORD` | Gmail app password               | Yes      | -                     |
| `GEMINI_API_KEY`     | Google Gemini AI API key         | Yes      | -                     |
| `DATABASE_URL`       | Database connection string       | No       | `sqlite:///./jobs.db` |

### **API Keys Setup**

#### **Gmail App Password**

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password for "Mail"
3. Use this password in `GMAIL_APP_PASSWORD`

#### **Google Gemini AI**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to `GEMINI_API_KEY`

## 🎮 Usage

### **Starting the Application**

```bash
# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Accessing the Application**

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### **Default Admin Account**

- **Username**: admin
- **Password**: admin123
- **Role**: Supervisor

## 🔌 API Endpoints

### **Authentication**

- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### **Job Management**

- `GET /jobs` - List all jobs
- `GET /jobs/{job_id}` - Get job details
- `POST /jobs` - Create new job
- `PUT /jobs/{job_id}` - Update job
- `DELETE /jobs/{job_id}` - Delete job

### **Job Scraping**

- `GET /scrape-jobs` - Manual job scraping page
- `POST /scrape-jobs` - Execute job scraping
- `GET /test-scraper` - Test scraper functionality

### **Resume Management**

- `GET /resume-builder` - Resume builder interface
- `POST /resume-builder` - Generate resume
- `GET /my-resumes` - User's resumes
- `GET /resume-preview/{resume_id}` - Preview resume

### **User Management**

- `GET /profile` - User profile
- `PUT /profile` - Update profile
- `GET /dashboard` - User dashboard
- `GET /new-jobs` - Recently added jobs

### **Applications**

- `POST /apply/{job_id}` - Apply for job
- `GET /my-applications` - User's applications
- `GET /view-applications/{job_id}` - View job applications

## 🗄️ Database Schema

### **Core Tables**

#### **Users Table**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    skills TEXT,
    is_supervisor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Jobs Table**

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    description TEXT,
    salary REAL,
    skills TEXT,
    experience_level VARCHAR,
    job_type VARCHAR,
    remote_policy VARCHAR,
    job_url VARCHAR,
    posted_by VARCHAR,
    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Applications Table**

```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    resume_path VARCHAR,
    cover_letter TEXT,
    status VARCHAR DEFAULT 'pending',
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Resumes Table**

```sql
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR NOT NULL,
    content TEXT,
    file_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 AI Components

### **Google Gemini AI Integration**

- **Resume Generation**: AI-powered resume content creation
- **Skill Extraction**: Intelligent skill identification
- **Content Optimization**: AI-driven content improvement
- **Personalization**: User-specific content generation

### **NLP Utilities**

- **Skill Matching**: Advanced skill comparison algorithms
- **Text Processing**: Intelligent text cleaning and formatting
- **Keyword Extraction**: Job description keyword analysis
- **Similarity Scoring**: Text similarity calculations

### **ATS Optimization**

- **Resume Scoring**: Comprehensive ATS compatibility scoring
- **Keyword Analysis**: Job description keyword matching
- **Format Validation**: ATS-friendly formatting checks
- **Improvement Suggestions**: Actionable optimization tips

## 🔍 Job Scraping

### **Scraping Sources**

- **Adzuna API**: Primary job data source
- **Real-time Updates**: Automated job collection
- **Smart Filtering**: Duplicate detection and filtering
- **Content Enhancement**: Full description fetching

### **Scraping Features**

- **Automated Scheduling**: Daily scraping at 11:30 AM and 4:00 PM
- **Duplicate Prevention**: Advanced duplicate detection
- **Content Cleaning**: Intelligent job description processing
- **Skill Extraction**: Automatic skill identification

### **Scraping Configuration**

```python
# Job titles and locations for auto-scraping
job_titles_locations = [
    ("Software Engineer", "delhi"),
    ("Full Stack Developer", "Chandigarh"),
    ("Python Developer", "delhi"),
    ("React Developer", "delhi"),
    ("Java Developer", "mohali"),
    # ... more combinations
]
```

## 📝 Resume Builder

### **AI-Powered Generation**

- **Content Creation**: AI-generated resume content
- **Skill Highlighting**: Intelligent skill emphasis
- **Professional Language**: Business-appropriate terminology
- **Customization**: User-specific content adaptation

### **PDF Generation**

- **Professional Templates**: Multiple layout options
- **ATS Optimization**: ATS-friendly formatting
- **Custom Styling**: Professional appearance
- **Export Options**: Multiple format support

### **Resume Features**

- **Skill Matching**: Job-specific skill emphasis
- **ATS Scoring**: Real-time ATS compatibility scoring
- **Content Suggestions**: AI-powered improvement tips
- **Version Control**: Multiple resume versions

## 🚀 Deployment

### **Production Setup**

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Docker Deployment**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables (Production)**

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Email Not Sending**

- Check Gmail app password configuration
- Verify `EMAIL_SENDER` and `GMAIL_APP_PASSWORD` in `.env`
- Ensure 2-factor authentication is enabled on Gmail

#### **AI Features Not Working**

- Verify `GEMINI_API_KEY` is set correctly
- Check internet connectivity for API calls
- Ensure API key has sufficient quota

#### **Database Errors**

- Verify database file permissions
- Check `DATABASE_URL` configuration
- Ensure SQLite is properly installed

#### **Job Scraping Issues**

- Check Adzuna API credentials
- Verify internet connectivity
- Review scraping logs for specific errors

### **Logs and Debugging**

```bash
# Enable debug logging
export LOG_LEVEL=debug

# Check application logs
tail -f app.log

# Test individual components
python -c "from app.scraper import fetch_adzuna_jobs; print(fetch_adzuna_jobs('Python Developer', 'Delhi'))"
```

## 🤝 Contributing

### **Development Setup**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Code Style**

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include error handling

### **Testing**

```bash
# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced AI capabilities
- **FastAPI** for the excellent web framework
- **SQLAlchemy** for robust database operations
- **Adzuna** for job data API

## 📞 Support

For support and questions:

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the API docs at `/docs`
- **Community**: Join our discussion forum

---

**Made with ❤️ by the Job Portal Team**
