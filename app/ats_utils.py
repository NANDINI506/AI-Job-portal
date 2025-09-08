"""
ATS (Applicant Tracking System) scoring utilities for resume analysis.
This module provides functions to analyze resumes and calculate ATS compatibility scores.
"""

import re
from typing import Dict, List, Tuple
from .nlp_utils import extract_skills, SKILLS_TAXONOMY

def calculate_ats_score(resume_text: str, job_description: str = None) -> Dict:
    """
    Calculate ATS compatibility score for a resume.
    
    Args:
        resume_text: The text content of the resume
        job_description: Optional job description to compare against
    
    Returns:
        Dictionary containing ATS score and detailed analysis
    """
    if not resume_text:
        return {
            'overall_score': 0,
            'formatting_score': 0,
            'keyword_score': 0,
            'contact_score': 0,
            'education_score': 0,
            'experience_score': 0,
            'skills_score': 0,
            'job_match_score': 0,
            'issues': ['No resume text provided'],
            'suggestions': ['Upload a valid resume file']
        }
    
    # Initialize scores
    scores = {
        'formatting_score': 0,
        'keyword_score': 0,
        'contact_score': 0,
        'education_score': 0,
        'experience_score': 0,
        'skills_score': 0,
        'job_match_score': 0
    }
    
    issues = []
    suggestions = []
    
    # 1. Formatting Analysis (25 points)
    formatting_score, formatting_issues, formatting_suggestions = analyze_formatting(resume_text)
    scores['formatting_score'] = formatting_score
    issues.extend(formatting_issues)
    suggestions.extend(formatting_suggestions)
    
    # 2. Contact Information (15 points)
    contact_score, contact_issues, contact_suggestions = analyze_contact_info(resume_text)
    scores['contact_score'] = contact_score
    issues.extend(contact_issues)
    suggestions.extend(contact_suggestions)
    
    # 3. Education (15 points)
    education_score, education_issues, education_suggestions = analyze_education(resume_text)
    scores['education_score'] = education_score
    issues.extend(education_issues)
    suggestions.extend(education_suggestions)
    
    # 4. Experience (20 points)
    experience_score, experience_issues, experience_suggestions = analyze_experience(resume_text)
    scores['experience_score'] = experience_score
    issues.extend(experience_issues)
    suggestions.extend(experience_suggestions)
    
    # 5. Skills (15 points)
    skills_score, skills_issues, skills_suggestions = analyze_skills(resume_text)
    scores['skills_score'] = skills_score
    issues.extend(skills_issues)
    suggestions.extend(skills_suggestions)
    
    # 6. Job Match (10 points) - if job description provided
    if job_description:
        job_match_score, job_match_issues, job_match_suggestions = analyze_job_match(resume_text, job_description)
        scores['job_match_score'] = job_match_score
        issues.extend(job_match_issues)
        suggestions.extend(job_match_suggestions)
    
    # Calculate overall score
    total_possible = 85 if job_description else 90
    overall_score = sum(scores.values())
    scores['overall_score'] = min(100, int((overall_score / total_possible) * 100))
    
    return {
        'overall_score': scores['overall_score'],
        **scores,
        'issues': issues,
        'suggestions': suggestions
    }

def analyze_formatting(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """Analyze resume formatting and structure."""
    score = 0
    issues = []
    suggestions = []
    
    # Check for proper sections
    sections = ['education', 'experience', 'skills', 'contact', 'summary', 'objective']
    found_sections = []
    
    for section in sections:
        if re.search(rf'\b{section}\b', resume_text.lower()):
            found_sections.append(section)
            score += 3
    
    # Check for bullet points
    bullet_points = len(re.findall(r'[•·▪▫◦‣⁃]\s', resume_text))
    if bullet_points >= 5:
        score += 5
    elif bullet_points >= 3:
        score += 3
    else:
        issues.append("Limited use of bullet points")
        suggestions.append("Use bullet points to highlight achievements and responsibilities")
    
    # Check for action verbs
    action_verbs = ['developed', 'implemented', 'managed', 'created', 'designed', 'analyzed', 
                   'improved', 'increased', 'decreased', 'coordinated', 'led', 'supervised']
    action_verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    if action_verb_count >= 5:
        score += 5
    elif action_verb_count >= 3:
        score += 3
    else:
        issues.append("Limited use of action verbs")
        suggestions.append("Use strong action verbs to describe your achievements")
    
    # Check for consistent formatting
    lines = resume_text.split('\n')
    if len(lines) > 20:
        score += 5
    else:
        issues.append("Resume may be too short")
        suggestions.append("Ensure your resume is comprehensive and detailed")
    
    # Check for professional language
    informal_words = ['gonna', 'wanna', 'gotta', 'cool', 'awesome', 'stuff']
    informal_count = sum(1 for word in informal_words if word in resume_text.lower())
    if informal_count == 0:
        score += 5
    else:
        issues.append("Contains informal language")
        suggestions.append("Use professional language throughout your resume")
    
    return min(25, score), issues, suggestions

def analyze_contact_info(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """Analyze contact information completeness."""
    score = 0
    issues = []
    suggestions = []
    
    # Check for email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, resume_text):
        score += 5
    else:
        issues.append("Email address not found")
        suggestions.append("Include a professional email address")
    
    # Check for phone number
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if re.search(phone_pattern, resume_text):
        score += 5
    else:
        issues.append("Phone number not found")
        suggestions.append("Include a phone number for contact")
    
    # Check for location/address
    location_indicators = ['street', 'avenue', 'road', 'city', 'state', 'zip', 'country']
    if any(indicator in resume_text.lower() for indicator in location_indicators):
        score += 3
    else:
        issues.append("Location information may be missing")
        suggestions.append("Include your city and state")
    
    # Check for LinkedIn or professional links
    linkedin_pattern = r'linkedin\.com'
    if re.search(linkedin_pattern, resume_text):
        score += 2
    else:
        suggestions.append("Consider adding your LinkedIn profile")
    
    return min(15, score), issues, suggestions

def analyze_education(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """Analyze education section."""
    score = 0
    issues = []
    suggestions = []
    
    # Check for degree information
    degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma', 'certificate']
    degree_found = any(keyword in resume_text.lower() for keyword in degree_keywords)
    if degree_found:
        score += 8
    else:
        issues.append("Degree information not clearly stated")
        suggestions.append("Clearly state your degree and field of study")
    
    # Check for institution name
    institution_keywords = ['university', 'college', 'institute', 'school']
    institution_found = any(keyword in resume_text.lower() for keyword in institution_keywords)
    if institution_found:
        score += 4
    else:
        issues.append("Institution name may be missing")
        suggestions.append("Include the name of your educational institution")
    
    # Check for graduation date or year
    year_pattern = r'\b(19|20)\d{2}\b'
    if re.search(year_pattern, resume_text):
        score += 3
    else:
        issues.append("Graduation date may be missing")
        suggestions.append("Include your graduation date or expected graduation")
    
    return min(15, score), issues, suggestions

def analyze_experience(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """Analyze work experience section."""
    score = 0
    issues = []
    suggestions = []
    
    # Check for job titles
    job_title_keywords = ['developer', 'engineer', 'manager', 'analyst', 'specialist', 'coordinator', 'assistant']
    job_titles_found = sum(1 for keyword in job_title_keywords if keyword in resume_text.lower())
    if job_titles_found >= 2:
        score += 8
    elif job_titles_found >= 1:
        score += 5
    else:
        issues.append("Job titles may not be clearly stated")
        suggestions.append("Clearly state your job titles and roles")
    
    # Check for company names
    company_indicators = ['inc', 'corp', 'ltd', 'company', 'llc', 'enterprises']
    companies_found = sum(1 for indicator in company_indicators if indicator in resume_text.lower())
    if companies_found >= 2:
        score += 6
    elif companies_found >= 1:
        score += 3
    else:
        issues.append("Company names may not be clearly stated")
        suggestions.append("Include company names for your work experience")
    
    # Check for dates
    date_pattern = r'\b(19|20)\d{2}\b'
    dates_found = len(re.findall(date_pattern, resume_text))
    if dates_found >= 4:
        score += 6
    elif dates_found >= 2:
        score += 3
    else:
        issues.append("Employment dates may be missing")
        suggestions.append("Include start and end dates for your positions")
    
    return min(20, score), issues, suggestions

def analyze_skills(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """Analyze skills section."""
    score = 0
    issues = []
    suggestions = []
    
    # Extract skills using existing NLP utils
    skills_dict = extract_skills(resume_text)
    all_skills = []
    for category_skills in skills_dict.values():
        all_skills.extend(category_skills)
    
    # Count technical skills
    technical_skills = len(all_skills)
    if technical_skills >= 10:
        score += 8
    elif technical_skills >= 5:
        score += 5
    elif technical_skills >= 3:
        score += 3
    else:
        issues.append("Limited technical skills listed")
        suggestions.append("Include more technical skills relevant to your field")
    
    # Check for skills section header
    if re.search(r'\bskills?\b', resume_text.lower()):
        score += 4
    else:
        issues.append("Skills section may not be clearly labeled")
        suggestions.append("Create a dedicated skills section")
    
    # Check for skill categorization
    if len(skills_dict) >= 3:
        score += 3
    else:
        suggestions.append("Consider categorizing your skills (e.g., Programming, Tools, Soft Skills)")
    
    return min(15, score), issues, suggestions

def analyze_job_match(resume_text: str, job_description: str) -> Tuple[int, List[str], List[str]]:
    """Analyze how well the resume matches a specific job description."""
    score = 0
    issues = []
    suggestions = []
    
    # Extract skills from both resume and job description
    resume_skills_dict = extract_skills(resume_text)
    job_skills_dict = extract_skills(job_description)
    
    resume_skills = set()
    for category_skills in resume_skills_dict.values():
        resume_skills.update(skill.lower() for skill in category_skills)
    
    job_skills = set()
    for category_skills in job_skills_dict.values():
        job_skills.update(skill.lower() for skill in category_skills)
    
    # Calculate skill match
    if job_skills:
        matching_skills = resume_skills.intersection(job_skills)
        match_percentage = len(matching_skills) / len(job_skills) * 100
        
        if match_percentage >= 70:
            score += 10
        elif match_percentage >= 50:
            score += 7
        elif match_percentage >= 30:
            score += 4
        else:
            score += 1
            issues.append(f"Low skill match with job requirements ({match_percentage:.1f}%)")
            suggestions.append("Add more skills that match the job requirements")
    
    # Check for keyword matching
    job_keywords = set(job_description.lower().split())
    resume_keywords = set(resume_text.lower().split())
    common_keywords = job_keywords.intersection(resume_keywords)
    
    if len(common_keywords) >= 10:
        score += 5
    elif len(common_keywords) >= 5:
        score += 3
    else:
        suggestions.append("Include more keywords from the job description")
    
    return min(10, score), issues, suggestions

def get_ats_grade(score: int) -> str:
    """Convert ATS score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    else:
        return "D" 