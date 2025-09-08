import spacy
import re
from sentence_transformers import SentenceTransformer
from typing import List, Set, Dict
import numpy as np
from pathlib import Path
import json

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not installed, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Initialize SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load predefined skills taxonomy
SKILLS_FILE = Path(__file__).parent / "data" / "skills_taxonomy.json"
if not SKILLS_FILE.parent.exists():
    SKILLS_FILE.parent.mkdir(parents=True)

# Default skills taxonomy if file doesn't exist
DEFAULT_SKILLS = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "C++", "Ruby", "PHP", "Swift", "Kotlin", "Go",
        "Rust", "TypeScript", "SQL", "R", "MATLAB", "Scala", "Perl", "Shell"
    ],
    "frameworks": [
        "React", "Angular", "Vue.js", "Django", "Flask", "Spring", "Node.js", "Express.js",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Cassandra", "Oracle",
        "Microsoft SQL Server", "Elasticsearch"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Docker", "Kubernetes"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Problem Solving", "Team Work", "Time Management",
        "Critical Thinking", "Adaptability", "Project Management", "Agile", "Scrum"
    ]
}

if not SKILLS_FILE.exists():
    with open(SKILLS_FILE, 'w') as f:
        json.dump(DEFAULT_SKILLS, f, indent=2)

with open(SKILLS_FILE, 'r') as f:
    SKILLS_TAXONOMY = json.load(f)

def normalize_text(text: str) -> str:
    """
    Normalize text for skill matching: lowercase, remove punctuation, extra spaces, and hyphens.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    return text.strip()

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text using SpaCy's NER.
    """
    doc = nlp(text)
    entities = {}
    
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    
    return entities

def extract_name(text: str) -> str:
    """
    Extract the person's name from resume text, avoiding locations, contact info, and known skills.
    """
    known_locations = {
        'chandigarh', 'mohali', 'punjab', 'delhi', 'bangalore', 'bengaluru', 'mumbai', 'pune', 'kolkata', 'hyderabad', 'gurgaon', 'noida', 'india', 'new delhi', 'chennai', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'bhopal', 'patna', 'vadodara', 'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar', 'allahabad', 'howrah', 'ranchi', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandrapur', 'solapur', 'hubli', 'mysore', 'tiruchirappalli', 'bareilly', 'aligarh', 'tiruppur', 'moradabad', 'gaya', 'jalgaon', 'kakinada', 'udupi', 'panipat', 'durgapur', 'siliguri', 'bokaro', 'kurnool', 'bellary', 'patiala', 'guntur', 'rohtak', 'bhavnagar', 'muzaffarnagar', 'mathura', 'kollam', 'kannur', 'kottayam', 'kozhikode', 'thrissur', 'palakkad', 'alappuzha', 'ernakulam', 'thiruvananthapuram', 'kerala', 'uttar pradesh', 'maharashtra', 'tamil nadu', 'karnataka', 'haryana', 'gujarat', 'west bengal', 'bihar', 'andhra pradesh', 'telangana', 'rajasthan', 'madhya pradesh', 'jharkhand', 'odisha', 'chhattisgarh', 'assam', 'goa', 'manipur', 'tripura', 'meghalaya', 'nagaland', 'mizoram', 'sikkim', 'arunachal pradesh', 'himachal pradesh', 'uttarakhand', 'jammu', 'kashmir'
    }
    known_skills = set()
    for cat in SKILLS_TAXONOMY.values():
        for skill in cat:
            known_skills.add(skill.lower())
    doc = nlp(text)
    lines = text.split('\n')[:20]  # Check first 20 lines for robustness
    # 1. Check the very first non-empty, all-uppercase, single-word line for name
    for line in lines:
        line = line.strip()
        if line:
            if line.isupper() and 1 <= len(line.split()) <= 2 and line.replace(' ', '').isalpha():
                if line.lower() not in known_locations and line.lower() not in known_skills:
                    return line.title()
            break  # Only check the first non-empty line
    # 2. Try to find a PERSON entity that is not a location, contact info, or skill
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if not any(label in [e.label_ for e in doc.ents if e.text == ent.text] for label in ["GPE", "LOC"]):
                if not re.search(r"\d|@|\.com|gmail|yahoo|hotmail|\+", ent.text):
                    if ent.text.lower() not in known_locations and ent.text.lower() not in known_skills:
                        return ent.text
    # 3. Look for common name patterns in the first few lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.search(r"\d|@|\.com|gmail|yahoo|hotmail|\+", line):
            continue
        if line.isupper() and len(line.split()) <= 3:
            continue  # likely a heading or location
        if line.lower() in known_locations or line.lower() in known_skills:
            continue
        name_pattern = r'^[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+$'
        if re.match(name_pattern, line):
            return line
        words = line.split()
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w):
            return line
    # 4. Fallback: return the first non-empty line that doesn't look like a location/contact/skill
    for line in lines:
        line = line.strip()
        if line and len(line.split()) <= 4 and not any(word.lower() in ['resume', 'cv', 'curriculum', 'vitae'] for word in line.split()):
            if not re.search(r"\d|@|\.com|gmail|yahoo|hotmail|\+", line):
                if line.lower() not in known_locations and line.lower() not in known_skills:
                    return line
    return None

def extract_education(text: str) -> str:
    """
    Extract education information from resume text, starting only after a standalone 'EDUCATION' heading.
    """
    degree_keywords = [
        'bachelor', 'master', 'phd', 'mba', 'b.tech', 'm.tech', 'ba', 'bs', 'ms', 'ma', 'msc', 'bca', 'mca', 'bsc', 'llb', 'llm', 'diploma', 'post graduation', 'graduation', 'senior secondary', 'high school'
    ]
    section_headings = [
        'objective', 'summary', 'experience', 'work experience', 'skills', 'projects', 'certifications', 'interests', 'hobbies', 'languages', 'profile', 'personal', 'contact', 'achievements', 'activities', 'references'
    ]
    
    # Date patterns to exclude
    date_patterns = [
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\s+(?:to|until|till|-)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\s+(?:to|until|till|-)\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b',
        r'\b\d{4}\s+(?:to|until|till|-)\s+\d{4}\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\s+(?:to|until|till|-)\s+\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{1,2}-\d{1,2}-\d{4}\s+(?:to|until|till|-)\s+\d{1,2}-\d{1,2}-\d{4}\b'
    ]
    
    lines = text.split('\n')
    education_lines = []
    in_education_section = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Start collecting only after a standalone 'EDUCATION' heading
        if not in_education_section and re.match(r'^education[:\s-]*$', line_stripped, re.IGNORECASE):
            in_education_section = True
            continue
            
        if in_education_section:
            # Stop at a new section heading
            if any(line_lower.startswith(h) for h in section_headings):
                break
                
            # Skip lines with email, phone, or URL
            if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", line):
                continue
            if re.search(r"(\+91[\-\s]?)?0?([6-9][0-9]{9})", line):
                continue
            if re.search(r"https?://", line):
                continue
                
            # Skip lines that are just date patterns
            is_date_only = False
            for pattern in date_patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    is_date_only = True
                    break
            
            if is_date_only:
                continue
                
            # Only include lines that:
            # - Start with a bullet or dash
            # - Are indented (start with whitespace)
            # - Contain degree/university keywords
            # - Are not too short (at least 5 words)
            if (line.strip().startswith(('•', '-', '*')) or
                line.startswith(' ') or
                any(degree in line_lower for degree in degree_keywords) or
                (len(line.split()) >= 5 and any(word in line_lower for word in ['school', 'college', 'university', 'institute', 'academy']))):
                education_lines.append(line.strip())
                
            # Optionally, stop after 7 lines to avoid capturing too much
            if len(education_lines) >= 7:
                break
                
    if education_lines:
        return "; ".join(education_lines)
    return None

def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extract skills from text by searching for matches from the skills taxonomy using normalization and partial matching.
    For skills with 1-2 characters, use exact word matching to avoid false positives.
    """
    found_skills = {category: [] for category in SKILLS_TAXONOMY.keys()}
    norm_text = normalize_text(text)
    words = set(norm_text.split())

    for category, skills in SKILLS_TAXONOMY.items():
        for skill in skills:
            norm_skill = normalize_text(skill)
            if len(norm_skill) <= 2:
                # Use exact word match for very short skills
                if norm_skill in words:
                    if skill not in found_skills[category]:
                        found_skills[category].append(skill)
            else:
                # Partial match for longer skills
                if norm_skill in norm_text:
                    if skill not in found_skills[category]:
                        found_skills[category].append(skill)
    return found_skills

def calculate_skill_match(job_skills: Dict[str, List[str]], 
                        resume_skills: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate the match percentage between job requirements and resume skills.
    """
    category_scores = {}
    
    for category in SKILLS_TAXONOMY.keys():
        job_category_skills = set(job_skills.get(category, []))
        resume_category_skills = set(resume_skills.get(category, []))
        
        if job_category_skills:
            matched_skills = job_category_skills.intersection(resume_category_skills)
            category_scores[category] = len(matched_skills) / len(job_category_skills) * 100
        else:
            # If no skills required in this category, it's a 100% match for the category
            category_scores[category] = 100.0
    
    # Calculate overall match percentage as an average of categories with required skills
    relevant_scores = [
        score for cat, score in category_scores.items()
        if job_skills.get(cat)
    ]
    
    if relevant_scores:
        category_scores['overall'] = sum(relevant_scores) / len(relevant_scores)
    else:
        # If no skills are required at all, the match is 100%
        category_scores['overall'] = 100.0
    
    return category_scores

def get_skill_suggestions(job_skills: Dict[str, List[str]], 
                         resume_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Generate skill improvement suggestions based on missing skills.
    """
    suggestions = {}
    
    for category in SKILLS_TAXONOMY.keys():
        job_category_skills = set(job_skills.get(category, []))
        resume_category_skills = set(resume_skills.get(category, []))
        
        missing_skills = job_category_skills - resume_category_skills
        if missing_skills:
            suggestions[category] = list(missing_skills)
    
    return suggestions

def extract_email(text: str) -> str:
    """
    Extract the first email address from resume text.
    """
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str:
    """
    Extract the first phone number from resume text (Indian format, flexible).
    """
    # Match +91 or 0 or nothing, then 10 digits
    match = re.search(r"(\+91[\-\s]?)?0?([6-9][0-9]{9})", text)
    if match:
        return match.group(0).replace(' ', '').replace('-', '')
    return None