import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
import re
import os
from .nlp_utils import extract_skills as nlp_extract_skills
from . import models
from .job_description_processor import clean_job_description, format_job_description, create_structured_description

# Get Adzuna API credentials from environment variables
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID', 'your-adzuna-app-id')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY', 'your-adzuna-app-key')
ADZUNA_COUNTRY = "in"  # Use 'in' for India, 'us' for USA, etc.

def normalize_text(text: str) -> str:
    """Normalize text for better duplicate detection."""
    if not text:
        return ""
    # Convert to lowercase and remove extra whitespace
    return re.sub(r'\s+', ' ', text.strip().lower())


def is_duplicate_job(job1: Dict, job2: Dict) -> bool:
    """Check if two jobs are duplicates using fuzzy matching."""
    # Normalize the data
    title1 = normalize_text(job1.get('title', ''))
    title2 = normalize_text(job2.get('title', ''))
    company1 = normalize_text(job1.get('company', ''))
    company2 = normalize_text(job2.get('company', ''))
    location1 = normalize_text(job1.get('location', ''))
    location2 = normalize_text(job2.get('location', ''))
    
    # Check for exact matches after normalization
    if title1 == title2 and company1 == company2 and location1 == location2:
        return True
    
    # Check for similar titles (common variations)
    title_similarity = calculate_similarity(title1, title2)
    if title_similarity > 0.9 and company1 == company2 and location1 == location2:
        return True
    
    return False


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings using simple algorithm."""
    if not str1 or not str2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def clean_salary(salary_text: str) -> float:
    """Convert salary text to float value."""
    if not salary_text:
        return 0.0
    
    # Extract numbers from salary text
    numbers = re.findall(r'\d+(?:,\d+)?', salary_text)
    if not numbers:
        return 0.0
    
    # Convert to float, removing commas
    return float(numbers[0].replace(',', ''))


def extract_skills(description: str) -> str:
    """Extract skills from job description using NLP."""
    try:
        # Use the new NLP-based skill extraction
        skills_dict = nlp_extract_skills(description)
        
        # Flatten the skills dictionary into a comma-separated string
        all_skills = []
        for category_skills in skills_dict.values():
            all_skills.extend(category_skills)
        
        return ', '.join(sorted(set(all_skills)))
    except Exception:
        return ""


def fetch_full_description_from_url(job_url: str) -> str:
    """
    Fetch the full job description from the job's URL.
    Simple and clean implementation.
    """
    if not job_url:
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Look for job description content
        job_content = soup.find('div', class_=lambda x: x and 'description' in x.lower() if x else False)
        if not job_content:
            job_content = soup.find('div', class_=lambda x: x and 'content' in x.lower() if x else False)
        
        if job_content:
            text = job_content.get_text(strip=True)
            if len(text) > 200:
                return clean_job_description(text)
        
        # Fallback: get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='main')
        if main_content:
            text = main_content.get_text(strip=True)
            if len(text) > 200:
                return clean_job_description(text)
        
        return ""
        
    except Exception:
        return ""


def create_professional_job_description(job_data: Dict) -> str:
    """
    Create a professional, structured job description.
    
    Args:
        job_data: Raw job data from API
        
    Returns:
        Professional formatted job description
    """
    title = job_data.get('title', '')
    company = job_data.get('company', '')
    location = job_data.get('location', '')
    description = job_data.get('description', '')
    salary = job_data.get('salary', 0)
    
    # Create structured description
    structured = create_structured_description(description)
    
    # Build professional job description
    sections = []
    
    # Job Header
    sections.append(f"**{title.upper()}**")
    sections.append(f"**Company:** {company}")
    sections.append(f"**Location:** {location}")
    if salary > 0:
        sections.append(f"**Salary:** ₹{salary:,.0f}/month")
    
    # Add extracted job details
    if structured.get('salary'):
        sections.append(f"**Package:** {structured['salary']}")
    if structured.get('job_type'):
        sections.append(f"**Job Type:** {structured['job_type'].title()}")
    if structured.get('work_location'):
        sections.append(f"**Work Location:** {structured['work_location']}")
    
    sections.append("")  # Empty line for spacing
    
    # Job Overview
    if structured.get('overview'):
        sections.append(f"**Job Overview:**\n{structured['overview']}")
        sections.append("")
    
    # Required Skills
    if structured.get('skills'):
        sections.append(f"**Required Skills:**\n{structured['skills']}")
        sections.append("")
    
    # Experience Required
    if structured.get('experience'):
        sections.append(f"**Experience Required:**\n{structured['experience']}")
        sections.append("")
    
    # Education
    if structured.get('education'):
        sections.append(f"**Education:**\n{structured['education']}")
        sections.append("")
    
    # Additional Details (if available)
    if description and len(description) > 100:
        # Clean and format the raw description
        cleaned_desc = clean_job_description(description)
        if cleaned_desc and len(cleaned_desc) > 50:
            sections.append(f"**Additional Details:**\n{cleaned_desc}")
    
    return '\n'.join(sections)


def create_job_with_preview(job_data: Dict) -> Dict[str, any]:
    """
    Create a job with both preview and full description.
    
    Args:
        job_data: Raw job data from API
        
    Returns:
        Job data with preview and full description
    """
    title = job_data.get('title', '')
    company = job_data.get('company', '')
    location = job_data.get('location', '')
    description = job_data.get('description', '')
    salary = job_data.get('salary', 0)
    job_url = job_data.get('url', '')
    
    # Create structured description
    structured = create_structured_description(description)
    
    # Create professional description
    professional_description = create_professional_job_description(job_data)
    
    # Extract skills
    try:
        skills = extract_skills(description)
    except Exception:
        skills = ''
    
    return {
        'title': title,
        'company': company,
        'location': location,
        'salary': salary,
        'skills': skills,
        'description': professional_description,  # Full professional description
        'description_preview': structured.get('preview', ''),  # Preview for cards
        'description_full': structured.get('full', ''),  # Full description
        'has_more': structured.get('has_more', False),  # Whether to show read more
        'url': job_url,
        'overview': structured.get('overview', ''),
        'experience': structured.get('experience', ''),
        'education': structured.get('education', ''),
        'job_type': structured.get('job_type', 'Full-time'),  # Default to Full-time
        'experience_level': structured.get('experience_level', 'Mid-Senior'),  # Default to Mid-Senior
        'remote_policy': structured.get('remote_policy', 'On-site'),  # Default to On-site
        'work_location': structured.get('work_location', '')
    }


def fetch_adzuna_jobs(job_title: str, location: str, num_pages: int = 1, results_per_page: int = 10) -> List[Dict]:
    """Fetch jobs from Adzuna API with professional job descriptions."""
    jobs = []
    
    for page in range(1, num_pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/{page}"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'what': job_title,
            'where': location,
            'results_per_page': results_per_page,
            'content-type': 'application/json'
        }
        
        try:
            print(f"Fetching Adzuna jobs: page {page}...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for job in data.get('results', []):
                title = job.get('title', '')
                company = job.get('company', {}).get('display_name', '')
                job_location = job.get('location', {}).get('display_name', '')
                description = job.get('description', '')
                salary = job.get('salary_min', 0.0) or 0.0
                job_url = job.get('redirect_url', '')
                
                # Try to get full description from URL if API description is short
                if len(description) < 1000 and job_url:
                    try:
                        full_description = fetch_full_description_from_url(job_url)
                        if full_description and len(full_description) > len(description):
                            description = full_description
                    except Exception:
                        # Silently continue if full description fetching fails
                        pass
                
                # Create job with preview and full description
                job_data = create_job_with_preview({
                    'title': title,
                    'company': company,
                    'location': job_location,
                    'description': description,
                    'salary': salary,
                    'url': job_url
                })
                
                # Check for duplicates within the current scraping session
                is_duplicate = False
                for existing_job in jobs:
                    if is_duplicate_job(job_data, existing_job):
                        print(f"Skipping duplicate job: {title} at {company}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                print(f"Adding job: {title} at {company}, {job_location}")
                jobs.append(job_data)
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error fetching Adzuna jobs page {page}: {e}")
            continue
    
    print(f"\nTotal jobs fetched from Adzuna: {len(jobs)}")
    return jobs


def scrape_linkedin_jobs(job_title: str, location: str, num_pages: int = 1) -> List[Dict]:
    """Fetch jobs from Adzuna API instead of LinkedIn."""
    return fetch_adzuna_jobs(job_title, location, num_pages=num_pages, results_per_page=10)


def notify_users_of_new_jobs(db, new_jobs):
    """Notify users about new job matches."""
    from .nlp_utils import extract_skills, calculate_skill_match
    from .email_utils import send_email
    from datetime import datetime, timedelta
    import os
    
    # Prevent duplicate notifications by checking if we've already notified for these jobs
    if not new_jobs:
        return
    
    # Create a unique identifier for this batch of jobs
    job_ids = [job.id if hasattr(job, 'id') else f"{job.get('title', '')}-{job.get('company', '')}-{job.get('location', '')}" for job in new_jobs]
    batch_id = "-".join(str(job_id) for job_id in job_ids)
    
    # Check if we've already sent notifications for this batch
    from . import models
    existing_notification = db.query(models.Notification).filter(
        models.Notification.title.like(f"%{len(new_jobs)} new jobs%"),
        models.Notification.created_at >= datetime.now() - timedelta(hours=1)
    ).first()
    
    if existing_notification:
        print(f"[Notification] Skipping duplicate notification for batch of {len(new_jobs)} jobs")
        return
    
    users = db.query(models.User).filter(models.User.is_supervisor == False).all()
    email_sender = os.environ.get('EMAIL_SENDER')
    email_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not email_sender or not email_password:
        print("[Email Warning] EMAIL_SENDER or GMAIL_APP_PASSWORD environment variable is missing. Emails will not be sent.")
    
    for user in users:
        user_skills_str = user.skills or ""
        if not user_skills_str.strip() or not user.email:
            print(f"[Email Skipped] User {user.username} ({user.email}) - No skills or email")
            continue
        
        user_skills_text = user_skills_str.replace(",", " ")
        user_skills = extract_skills(user_skills_text)
        matched_jobs = []
        
        for job in new_jobs:
            job_text = (job.description or "") + " " + (job.skills or "")
            job_skills = extract_skills(job_text)
            match_scores = calculate_skill_match(job_skills, user_skills)
            score = match_scores.get('overall', 0)
            
            # Lower threshold to 30% to catch more matches
            if score > 30:
                matched_jobs.append((job, score))
        
        if matched_jobs:
            # Sort by match score (highest first) and limit to 5 jobs for email
            matched_jobs.sort(key=lambda x: x[1], reverse=True)
            email_jobs = matched_jobs[:5]  # Show only top 5 jobs in email
            
            subject = f"New Job Matches from Recent Scraping"
            body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1a73e8; margin-bottom: 20px;">🎯 New Job Matches for You!</h2>
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    Dear {user.full_name or user.username},
                </p>
                <p style="font-size: 14px; color: #666; margin-bottom: 25px;">
                    We found <strong>{len(matched_jobs)} new jobs</strong> that match your skills! 
                    Here are the top {len(email_jobs)} matches:
                </p>
            """
            
            for i, (job, score) in enumerate(email_jobs, 1):
                # Use the preview description for email
                desc_snippet = job.description_preview if hasattr(job, 'description_preview') and job.description_preview else (job.description[:200] + '...' if job.description and len(job.description) > 200 else (job.description or ''))
                body += f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fafafa;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <h3 style="color: #1a73e8; margin: 0; font-size: 16px;">{job.title}</h3>
                        <span style="background: #34a853; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                            {score:.0f}% Match
                        </span>
                    </div>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;"><strong>{job.company}</strong></p>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;">📍 {job.location}</p>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;">💰 ₹{job.salary:,.0f}/month</p>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;">🛠️ Skills: {job.skills}</p>
                    <div style="background: white; padding: 10px; border-radius: 4px; margin-top: 10px;">
                        <pre style="margin: 0; font-family: Arial, sans-serif; font-size: 12px; color: #333; white-space: pre-wrap;">{desc_snippet}</pre>
                    </div>
                </div>
                """
            
            # Add "View All New Jobs" button
            if len(matched_jobs) > 5:
                base_url = os.environ.get('BASE_URL', 'http://localhost:8000')
                body += f"""
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{base_url}/new-jobs" 
                       style="background: #1a73e8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        🔍 View All {len(matched_jobs)} New Jobs
                    </a>
                </div>
                <p style="text-align: center; color: #666; font-size: 14px;">
                    Login to your profile to apply and see more details
                </p>
                """
            
            body += """
                <div style="margin-top: 25px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                    <p style="color: #666; font-size: 14px; margin: 0;">
                        Best regards,<br>
                        <strong>Job Portal Team</strong>
                    </p>
                </div>
            </div>
            """
            
            try:
                if email_sender and email_password:
                    send_email(user.email, subject, body)
                    print(f"[Email Sent] To: {user.email}, Jobs: {len(matched_jobs)} (showing top {len(email_jobs)} in email)")
                else:
                    print(f"[Email Skipped] Would send to: {user.email}, but email credentials are missing.")
            except Exception as e:
                print(f"[Email Error] Failed to send to {user.email}: {e}")
        else:
            print(f"[Email Skipped] User {user.username} ({user.email}) - No matching jobs found (threshold: 30%)")
    
    # Log notification completion
    total_emails_sent = sum(1 for user in users if user.skills and user.email)
    print(f"[Notification Complete] Sent notifications for {len(new_jobs)} new jobs to {total_emails_sent} users") 
