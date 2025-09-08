"""
Professional Job Description Processor

Creates clean, structured job descriptions like professional job portals.
"""

import re
from typing import Dict, List, Optional


def clean_job_description(text: str) -> str:
    """
    Clean raw job description text and create professional formatting.
    
    Args:
        text: Raw job description text
        
    Returns:
        Cleaned, professional text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace common HTML entities
    html_entities = {
        '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>',
        '&quot;': '"', '&#39;': "'", '&rsquo;': "'", '&lsquo;': "'",
        '&mdash;': '—', '&ndash;': '–', '&hellip;': '...'
    }
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    # Remove common job board artifacts
    artifacts = [
        r'Apply for this job.*?(?=\n|\.|$)',
        r'Back to.*?search.*?(?=\n|\.|$)',
        r'Create alert.*?(?=\n|\.|$)',
        r'Share this job.*?(?=\n|\.|$)',
        r'Report this job.*?(?=\n|\.|$)',
        r'Show (Less|More).*?(?=\n|\.|$)',
        r'Posted.*?ago.*?(?=\n|\.|$)',
        r'Job ID.*?(?=\n|\.|$)',
        r'Reference.*?(?=\n|\.|$)',
        r'Similar jobs.*?(?=\n|\.|$)',
        r'Terms & Conditions.*?(?=\n|\.|$)',
        r'Privacy Notice.*?(?=\n|\.|$)',
        r'Cookie Use.*?(?=\n|\.|$)',
        r'Popular searches.*?(?=\n|\.|$)',
    ]
    
    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text


def format_job_description(text: str) -> str:
    """
    Format cleaned job description into professional structure.
    
    Args:
        text: Cleaned job description text
        
    Returns:
        Professionally formatted text
    """
    if not text:
        return ""
    
    # Split into sentences for better processing
    sentences = re.split(r'[.!?]+', text)
    clean_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:
            # Clean up common formatting issues
            sentence = re.sub(r'<[^>]+>', '', sentence)  # Remove any remaining HTML
            sentence = re.sub(r'\s+', ' ', sentence)  # Normalize whitespace
            clean_sentences.append(sentence)
    
    # Create structured sections
    sections = []
    
    # Overview section (first few sentences)
    if clean_sentences:
        overview = '. '.join(clean_sentences[:3]) + '.'
        sections.append(f"**Job Overview:**\n{overview}")
    
    # Skills section (extract from text)
    skills = extract_skills_from_text(text)
    if skills:
        sections.append(f"**Required Skills:**\n{skills}")
    
    # Experience section (if mentioned)
    experience = extract_experience_from_text(text)
    if experience:
        sections.append(f"**Experience Required:**\n{experience}")
    
    # Education section (if mentioned)
    education = extract_education_from_text(text)
    if education:
        sections.append(f"**Education:**\n{education}")
    
    # Join sections with proper spacing
    return '\n\n'.join(sections)


def create_preview_and_full_description(text: str, preview_length: int = 300) -> Dict[str, str]:
    """
    Create both preview and full description with read more functionality.
    
    Args:
        text: Full job description text
        preview_length: Length of preview text
        
    Returns:
        Dictionary with preview and full description
    """
    if not text:
        return {"preview": "", "full": "", "has_more": False}
    
    # Clean the text first
    cleaned_text = clean_job_description(text)
    
    if len(cleaned_text) <= preview_length:
        return {
            "preview": cleaned_text,
            "full": cleaned_text,
            "has_more": False
        }
    
    # Find a good break point (end of sentence)
    preview_text = cleaned_text[:preview_length]
    last_period = preview_text.rfind('.')
    last_exclamation = preview_text.rfind('!')
    last_question = preview_text.rfind('?')
    
    # Find the latest sentence ending
    break_point = max(last_period, last_exclamation, last_question)
    
    if break_point > preview_length * 0.7:  # If we can find a good break point
        preview_text = cleaned_text[:break_point + 1]
    
    return {
        "preview": preview_text,
        "full": cleaned_text,
        "has_more": True
    }


def extract_skills_from_text(text: str) -> str:
    """Extract and format skills from job description."""
    # Common skill patterns
    skill_patterns = [
        r'(?:experience with|knowledge of|proficient in|expertise in)\s+([^.!?]+)',
        r'(?:skills?|technologies?|tools?|frameworks?|languages?)\s*[:\-]\s*([^.!?]+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Developer|Engineer|Analyst|Specialist)',
        r'(?:Python|Java|JavaScript|React|Angular|Node\.js|Django|Flask|Spring|AWS|Azure|Docker|Kubernetes|MySQL|PostgreSQL|MongoDB)',
        r'(?:HTML|CSS|SQL|Git|Jenkins|JIRA|Agile|Scrum|DevOps|Machine Learning|AI|Data Science)',
    ]
    
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 3:
                skills.append(match.strip())
    
    # Remove duplicates and format
    unique_skills = list(set(skills))
    if unique_skills:
        return '• ' + '\n• '.join(unique_skills[:15])  # Limit to 15 skills
    return ""


def extract_experience_from_text(text: str) -> str:
    """Extract experience requirements from job description."""
    experience_patterns = [
        r'(\d+\s*[-+]\s*\d+\s*years?\s+experience)',
        r'(?:minimum|at least|minimum of)\s+(\d+\s*years?\s+experience)',
        r'(?:entry\s*level|junior|senior|mid\s*level|experienced)',
        r'(?:fresher|graduate|0\s*-\s*2\s*years|2\s*-\s*4\s*years|4\s*\+\s*years)',
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    
    return ""


def extract_education_from_text(text: str) -> str:
    """Extract education requirements from job description."""
    education_patterns = [
        r'(?:Bachelor|Master|PhD|Degree|Diploma)\s+(?:in|of)\s+([^.!?]+)',
        r'(?:Computer Science|Engineering|Mathematics|Statistics|Data Science|Information Technology)',
        r'(?:related\s+field|equivalent\s+experience|any\s+graduate)',
        r'(?:B\.Tech|M\.Tech|B\.E|M\.E|BCA|MCA|BSc|MSc)',
    ]
    
    for pattern in education_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    
    return ""


def extract_job_details(text: str) -> Dict[str, str]:
    """Extract comprehensive job details from text."""
    details = {}
    
    # Extract salary information
    salary_patterns = [
        r'(\d+(?:\.\d+)?\s*[-+]\s*\d+(?:\.\d+)?\s*lacs?/annum)',
        r'(\d+(?:\.\d+)?\s*[-+]\s*\d+(?:\.\d+)?\s*LPA)',
        r'(?:salary|CTC|package)\s*[:\-]\s*([^.!?]+)',
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details['salary'] = match.group(1) if match.groups() else match.group(0)
            break
    
    # Extract experience level
    experience_patterns = [
        (r'(?:fresher|0\s*[-+]\s*1\s*year|entry\s*level|graduate)', 'Entry-level'),
        (r'(?:junior|1\s*[-+]\s*3\s*year)', 'Junior'),
        (r'(?:2\s*[-+]\s*5\s*year|mid\s*level)', 'Mid-level'),
        (r'(?:senior|5\s*[-+]\s*8\s*year|lead)', 'Senior'),
        (r'(?:8\+\s*year|principal|architect|manager)', 'Principal/Manager'),
    ]
    
    for pattern, level in experience_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            details['experience_level'] = level
            break
    
    # Extract job type
    job_type_patterns = [
        (r'full[\s-]*time', 'Full-time'),
        (r'part[\s-]*time', 'Part-time'),
        (r'contract|contractual', 'Contract'),
        (r'freelance', 'Freelance'),
        (r'internship|intern', 'Internship'),
        (r'temporary|temp', 'Temporary'),
    ]
    
    for pattern, job_type in job_type_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            details['job_type'] = job_type
            break
    
    # Extract remote policy
    remote_patterns = [
        (r'(?:work\s*from\s*home|remote|100%\s*remote)', 'Remote'),
        (r'(?:hybrid|flexible|remote\s*and\s*office)', 'Hybrid'),
        (r'(?:on[\s-]*site|office|in[\s-]*person)', 'On-site'),
    ]
    
    for pattern, policy in remote_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            details['remote_policy'] = policy
            break
    
    # Extract location details
    location_patterns = [
        r'(?:location|work\s*from|office)\s*[:\-]\s*([^.!?]+)',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details['work_location'] = match.group(1) if match.groups() else match.group(0)
            break
    
    return details


def create_structured_description(text: str) -> Dict[str, any]:
    """
    Create structured job description data.
    
    Args:
        text: Job description text
        
    Returns:
        Dictionary with structured data
    """
    cleaned_text = clean_job_description(text)
    formatted_text = format_job_description(cleaned_text)
    preview_full = create_preview_and_full_description(cleaned_text)
    job_details = extract_job_details(cleaned_text)
    
    return {
        'raw_text': text,
        'cleaned_text': cleaned_text,
        'formatted_text': formatted_text,
        'preview': preview_full['preview'],
        'full': preview_full['full'],
        'has_more': preview_full['has_more'],
        'overview': extract_overview(cleaned_text),
        'skills': extract_skills_from_text(cleaned_text),
        'experience': extract_experience_from_text(cleaned_text),
        'education': extract_education_from_text(cleaned_text),
        'salary': job_details.get('salary', ''),
        'job_type': job_details.get('job_type', ''),
        'experience_level': job_details.get('experience_level', ''),
        'remote_policy': job_details.get('remote_policy', ''),
        'work_location': job_details.get('work_location', '')
    }


def extract_overview(text: str) -> str:
    """Extract job overview from text."""
    sentences = re.split(r'[.!?]+', text)
    overview_sentences = []
    
    for sentence in sentences[:3]:  # First 3 sentences
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:
            overview_sentences.append(sentence)
    
    if overview_sentences:
        return '. '.join(overview_sentences) + '.'
    return ""


def truncate_description(text: str, max_length: int = 200) -> str:
    """
    Truncate description to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can find a good break point
        truncated = truncated[:last_space]
    
    return truncated + '...'


def to_html(text: str) -> str:
    """
    Convert text to simple HTML format.
    
    Args:
        text: Text to convert
        
    Returns:
        HTML formatted text
    """
    if not text:
        return ""
    
    # Convert line breaks to HTML
    html_text = text.replace('\n\n', '</p><p>')
    html_text = f'<p>{html_text}</p>'
    
    # Convert bullet points
    html_text = re.sub(r'^[•\-\*]\s*', '<li>', html_text, flags=re.MULTILINE)
    html_text = re.sub(r'\n[•\-\*]\s*', '</li>\n<li>', html_text)
    
    # Wrap lists in ul tags
    if '<li>' in html_text:
        html_text = html_text.replace('<p><li>', '<p><ul><li>')
        html_text = html_text.replace('</li></p>', '</li></ul></p>')
    
    return html_text
