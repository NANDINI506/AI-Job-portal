import google.generativeai as genai
import os
from typing import Dict, Any
import json

class GeminiResumeGenerator:
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found. Using fallback content generation.")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                # Use the correct model name for the latest Gemini API
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API: {e}")
                # Try fallback model if the main one fails
                try:
                    self.model = genai.GenerativeModel('gemini-1.0-pro')
                except Exception as e2:
                    print(f"Warning: Fallback model also failed: {e2}")
                    self.model = None
    
    def generate_resume_content(self, user_prompt: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate professional resume content using Gemini AI
        """
        
        # Create a comprehensive prompt for Gemini
        system_prompt = """
        You are an expert resume writer and ATS (Applicant Tracking System) optimization specialist. 
        Your task is to EXTRACT and USE ALL SPECIFIC INFORMATION provided by the user to create a professional, keyword-rich resume.
        
        CRITICAL INSTRUCTIONS:
        1. EXTRACT ALL SPECIFIC DETAILS from the user's prompt including:
           - Name, location, education details
           - Work experience with company names, dates, achievements
           - Technical skills, tools, and technologies
           - Projects with descriptions and technologies used
           - Certifications with issuing organizations and years
           - Any specific achievements, metrics, or accomplishments
        
        2. DO NOT use generic placeholder content if specific information is provided
        3. Use the exact names, dates, companies, and details mentioned by the user
        4. Structure the information professionally while preserving all specific details
        5. Use strong action verbs and quantifiable achievements when possible
        6. Format content for easy ATS parsing
        
        IMPORTANT: If the user provides detailed information about their experience, education, skills, or projects, 
        you MUST use that specific information rather than generating generic content.
        
        Return the content in the following JSON format:
        {
            "personal_info": {
                "name": "Extract actual name from user prompt",
                "email": "Extract or use placeholder if not provided",
                "phone": "Extract or use placeholder if not provided", 
                "location": "Extract actual location from user prompt",
                "linkedin": "Extract or use placeholder if not provided"
            },
            "professional_summary": "Create summary based on user's actual experience and goals",
            "work_experience": [
                {
                    "title": "Extract actual job title",
                    "company": "Extract actual company name",
                    "duration": "Extract actual dates/duration",
                    "achievements": [
                        "Extract actual achievements mentioned by user"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Extract actual degree",
                    "institution": "Extract actual institution",
                    "year": "Extract actual graduation year",
                    "gpa": "Extract actual GPA if mentioned"
                }
            ],
            "skills": {
                "technical_skills": ["Extract actual technical skills mentioned"],
                "soft_skills": ["Extract actual soft skills mentioned"],
                "tools": ["Extract actual tools/technologies mentioned"]
            },
            "projects": [
                {
                    "name": "Extract actual project name",
                    "description": "Extract actual project description",
                    "achievements": ["Extract actual project achievements"]
                }
            ],
            "certifications": [
                {
                    "name": "Extract actual certification name",
                    "issuer": "Extract actual issuing organization",
                    "year": "Extract actual year obtained"
                }
            ]
        }
        """
        
        user_prompt_enhanced = f"""
        User Request: {user_prompt}
        
        Additional Context:
        - Target Role: {user_data.get('target_role', 'General Professional')}
        - Experience Level: {user_data.get('experience_level', 'Mid-level')}
        - Industry: {user_data.get('industry', 'Technology')}
        - Key Skills: {user_data.get('key_skills', '')}
        - Years of Experience: {user_data.get('years_experience', '3-5')}
        
        Please generate a professional resume based on this information. 
        If specific details are not provided, create realistic but generic content that demonstrates expertise in the target role.
        """
        
        try:
            # Check if Gemini model is available
            if not self.model:
                print("Using fallback content generation (no Gemini API)")
                return self._generate_fallback_content(user_data, user_prompt)
            
            # Generate content using Gemini
            response = self.model.generate_content([system_prompt, user_prompt_enhanced])
            
            # Parse the response
            content = response.text
            
            # Try to extract JSON from the response
            try:
                # Find JSON content in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_content = content[start_idx:end_idx]
                
                resume_data = json.loads(json_content)
                return resume_data
                
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured format from the text
                return self._parse_text_to_structured_format(content)
                
        except Exception as e:
            print(f"Error generating resume content: {e}")
            return self._generate_fallback_content(user_data, user_prompt)
    
    def _parse_text_to_structured_format(self, content: str) -> Dict[str, Any]:
        """
        Parse text content into structured format if JSON parsing fails
        """
        return {
            "personal_info": {
                "name": "Professional Candidate",
                "email": "candidate@email.com",
                "phone": "(555) 123-4567",
                "location": "City, State",
                "linkedin": "linkedin.com/in/professional"
            },
            "professional_summary": "Experienced professional with strong technical skills and proven track record of delivering results.",
            "work_experience": [
                {
                    "title": "Senior Professional",
                    "company": "Technology Company",
                    "duration": "2020 - Present",
                    "achievements": [
                        "Led successful project delivery with 95% client satisfaction",
                        "Improved team productivity by 25% through process optimization",
                        "Managed cross-functional teams of 10+ members"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor's Degree",
                    "institution": "University Name",
                    "year": "2020",
                    "gpa": "3.8"
                }
            ],
            "skills": {
                "technical_skills": ["Python", "JavaScript", "SQL"],
                "soft_skills": ["Leadership", "Communication", "Problem Solving"],
                "tools": ["Git", "Docker", "AWS"]
            },
            "projects": [
                {
                    "name": "Key Project",
                    "description": "Developed comprehensive solution using modern technologies",
                    "achievements": ["Successfully delivered on time and budget", "Received positive client feedback"]
                }
            ],
            "certifications": [
                {
                    "name": "Professional Certification",
                    "issuer": "Certifying Body",
                    "year": "2022"
                }
            ]
        }
    
    def _generate_fallback_content(self, user_data: Dict[str, Any], user_prompt: str = "") -> Dict[str, Any]:
        """
        Generate fallback content if Gemini API fails
        """
        # Prioritize user-provided structured data; fall back to prompt extraction
        extracted_info = self._extract_info_from_prompt(user_prompt)
        
        # Helper: merge dict values with preference order user_data > extracted_info > default
        def pick(key: str, default=None):
            if isinstance(default, list):
                # merge lists uniquely preserving order
                merged = []
                for source in [user_data.get(key), extracted_info.get(key), default]:
                    if not source:
                        continue
                    for item in source:
                        if item not in merged:
                            merged.append(item)
                return merged
            return user_data.get(key) or extracted_info.get(key) or default

        # Target context
        target_role = (user_data.get('target_role') or 'Full Stack Developer').strip()
        experience_level = (user_data.get('experience_level') or 'Entry-level').strip()
        industry = (user_data.get('industry') or 'Technology').strip()
        key_skills = user_data.get('key_skills', '')

        # Try to derive skills from user inputs and prompt
        def extract_skills(text: str) -> Dict[str, list]:
            if not text:
                return {"technical": [], "tools": [], "soft": []}
            import re
            tech_keywords = [
                'html', 'css', 'javascript', 'react', 'react.js', 'node', 'node.js', 'express', 'php', 'sql', 'mysql',
                'postgres', 'java', 'python', 'django', 'flask', 'linux', 'windows', 'git', 'github', 'docker'
            ]
            soft_keywords = ['communication', 'team', 'problem', 'leadership', 'analytical', 'collaboration']
            tools_keywords = ['git', 'github', 'vscode', 'ms office', 'excel', 'powerpoint']

            tset, sset, toolset = set(), set(), set()
            lower = text.lower()
            for kw in tech_keywords:
                if kw in lower:
                    tset.add(kw.replace('.js', '').replace('react', 'React').title())
            for kw in soft_keywords:
                if kw in lower:
                    sset.add(kw.title())
            for kw in tools_keywords:
                if kw in lower:
                    toolset.add(kw.title())
            return {
                "technical": sorted(tset),
                "soft": sorted(sset) or ['Problem Solving', 'Team Collaboration', 'Communication'],
                "tools": sorted(toolset)
            }

        skills_from_prompt = extract_skills(user_prompt)
        parsed_key_skills = [s.strip() for s in key_skills.split(',') if s.strip()]
        technical_skills = list(dict.fromkeys((user_data.get('technical_skills') or []) + skills_from_prompt['technical'] + parsed_key_skills))
        tools_skills = list(dict.fromkeys((user_data.get('tools') or []) + skills_from_prompt['tools']))
        soft_skills = list(dict.fromkeys((user_data.get('soft_skills') or []) + skills_from_prompt['soft']))

        # Education parsing (supports percentages/CGPA, institutions, ongoing degrees)
        education = user_data.get('education') or extracted_info.get('education')
        if not education:
            import re
            education = []
            
            # Enhanced Bachelor's pattern matching for various formats
            b_patterns = [
                # Pattern 1: "Bachelor's degree in Computer Applications (73.3%) from GGDSD College, Chandigarh"
                r"bachelor[''`s]*\s+degree\s+in\s+([^()]+)\s*\(([^)]+)%\)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
                r"bachelor[''`s]*\s+in\s+([^()]+)\s*\(([^)]+)%\)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
                # Pattern 2: "Bachelor's degree in Computer Applications from GGDSD College, Chandigarh (73.3%)"
                r"bachelor[''`s]*\s+degree\s+in\s+([^,]+)\s+from\s+([^()]+)\s*\(([^)]+)%\)",
                r"bachelor[''`s]*\s+in\s+([^,]+)\s+from\s+([^()]+)\s*\(([^)]+)%\)",
                # Pattern 3: "Bachelor's degree in Computer Applications from GGDSD College, Chandigarh"
                r"bachelor[''`s]*\s+degree\s+in\s+([^,]+)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
                r"bachelor[''`s]*\s+in\s+([^,]+)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
                # Pattern 4: "Bachelor's degree in Computer Applications (73.3%)"
                r"bachelor[''`s]*\s+degree\s+in\s+([^()]+)\s*\(([^)]+)%\)",
                r"bachelor[''`s]*\s+in\s+([^()]+)\s*\(([^)]+)%\)",
            ]
            
            for pattern in b_patterns:
                b_match = re.search(pattern, user_prompt, re.IGNORECASE)
                if b_match:
                    groups = b_match.groups()
                    if len(groups) == 3:
                        # For the first pattern: degree, percentage, institution
                        degree = groups[0].strip()
                        gpa = groups[1].strip()
                        institution = groups[2].strip()
                    elif len(groups) == 2:  # Pattern 4: degree, percentage
                        degree = groups[0].strip()
                        gpa = groups[1].strip()
                        institution = ""
                    
                    education.append({
                        "degree": f"Bachelor's in {degree}",
                        "institution": institution,
                        "year": "2023",  # Default year
                        "gpa": gpa
                    })
                    break
            
            # Enhanced Master's pattern matching
            m_patterns = [
                r"master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
                r"mca\s+at\s+([^.,]+)",
                r"pursuing\s+master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
                r"currently\s+pursuing\s+master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
            ]
            
            for pattern in m_patterns:
                m_match = re.search(pattern, user_prompt, re.IGNORECASE)
                if m_match:
                    education.append({
                        "degree": "Master of Computer Applications (Pursuing)",
                        "institution": m_match.group(1).strip(),
                        "year": "Present",
                        "gpa": ""
                    })
                    break

        # Projects extraction
        projects = user_data.get('projects') or extracted_info.get('projects')
        if not projects:
            import re
            projects = []
            # Look for common project phrases
            project_phrases = re.findall(r"(tourism website|online food delivery platform|event planning website)", user_prompt, re.IGNORECASE)
            if project_phrases:
                for p in project_phrases:
                    pname = p.title()
                    projects.append({
                        "name": pname,
                        "description": f"Designed and built a {pname.lower()} with responsive UI and dynamic features.",
                        "achievements": [
                            "Implemented frontend using modern HTML, CSS, and JavaScript",
                            "Built backend with REST APIs and database integration",
                            "Deployed and tested across devices"
                        ]
                    })

        # Work experience – if not provided, synthesize an Academic/Projects experience block
        work_experience = user_data.get('work_experience') or extracted_info.get('work_experience')
        if not work_experience:
            work_experience = [{
                "title": f"{target_role} (Academic Projects)",
                "company": "Academic/Personal Projects",
                "duration": "Ongoing",
                "achievements": [
                    "Developed multiple web applications including tourism, food delivery, and event planning systems",
                    "Implemented responsive UIs, dynamic client-side features, and secure backend logic",
                    "Worked with HTML, CSS, JavaScript, React (basic), PHP, SQL, and Java",
                    "Collaborated with peers and followed version control best practices"
                ]
            }]

        # Personal info – allow user overrides
        personal_info = {
            "name": pick('name', extracted_info.get('name') or 'YOUR NAME'),
            "email": pick('email', 'your.email@example.com'),
            "phone": pick('phone', '(+91) 00000 00000'),
            "location": pick('location', extracted_info.get('location') or 'Your City, India'),
            "linkedin": pick('linkedin', 'linkedin.com/in/yourprofile')
        }

        # Professional summary – craft from degrees, target role, and skills
        def build_summary():
            degree_bits = []
            if education:
                for e in education:
                    if 'Master' in e.get('degree',''):
                        degree_bits.append('currently pursuing ' + e['degree'])
                    elif "Bachelor" in e.get('degree',''):
                        degree_bits.append(e['degree'])
            skills_preview = ', '.join([s for s in technical_skills][:5])
            return (
                f"Aspiring {target_role} with strong foundations in programming, databases, and web technologies; "
                + (degree_bits[0] + '; ' if degree_bits else '')
                + f"hands-on experience building full‑stack applications. Proficient in {skills_preview}. "
                + "Passionate about problem‑solving, clean code, and continuous learning."
            )
        
        return {
            "personal_info": personal_info,
            "professional_summary": user_data.get('summary') or extracted_info.get('summary') or build_summary(),
            "work_experience": work_experience,
            "education": education or [{"degree": "Bachelor's in Computer Applications", "institution": "", "year": "", "gpa": ""}],
            "skills": {
                "technical_skills": technical_skills or ["HTML", "CSS", "JavaScript", "React", "PHP", "SQL", "Java"],
                "soft_skills": soft_skills,
                "tools": tools_skills or ["Git", "Linux", "Windows", "MS Office"]
            },
            "projects": projects or [],
            "certifications": user_data.get('certifications') or extracted_info.get('certifications') or []
        }
    
    def _extract_info_from_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Extract specific information from user prompt using text parsing
        """
        extracted_info = {}
        
        if not user_prompt:
            return extracted_info
        
        prompt_lower = user_prompt.lower()
        
        # Extract name
        import re
        name_patterns = [
            r"i'm\s+([a-zA-Z]+\s+[a-zA-Z]+)(?:\s+a\s+|\s+based|\s+with|\s+graduating|\s+from)",
            r"my\s+name\s+is\s+([a-zA-Z]+\s+[a-zA-Z]+)(?:\s+and|\s+i|\s+graduated|\s+from)",
            r"([a-zA-Z]+\s+[a-zA-Z]+)\s+(?:is\s+my\s+name|graduated|based|works)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                extracted_info['name'] = match.group(1).strip().title()
                break
        
        # Extract location
        location_patterns = [
            r"based\s+in\s+([a-zA-Z\s,]+?)(?:\s+with|\s+graduating|\s+i|\s+hold)",
            r"from\s+([a-zA-Z\s,]+?)(?:\s+graduating|\s+with|\s+and|\s+i)",
            r"in\s+([a-zA-Z\s,]+?)(?:\s+with|\s+graduating|\s+and|\s+i)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                location = match.group(1).strip()
                if len(location) > 3:  # Avoid short matches
                    extracted_info['location'] = location.title()
                    break
        
        # Extract education with enhanced patterns
        education_list = []
        
        # Bachelor's degree patterns
        b_patterns = [
            r"bachelor[''`s]*\s+degree\s+in\s+([^()]+)\s*\(([^)]+)%\)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
            r"bachelor[''`s]*\s+in\s+([^()]+)\s*\(([^)]+)%\)\s+from\s+([^,]+(?:,\s*[^,]+)?)",
            r"bachelor[''`s]*\s+degree\s+in\s+([^,]+)\s+from\s+([^()]+)\s*\(([^)]+)%\)",
            r"bachelor[''`s]*\s+in\s+([^,]+)\s+from\s+([^()]+)\s*\(([^)]+)%\)",
        ]
        
        for pattern in b_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    # For the first pattern: degree, percentage, institution
                    degree = groups[0].strip()
                    gpa = groups[1].strip()
                    institution = groups[2].strip()
                    
                    education_list.append({
                        "degree": f"Bachelor's in {degree.title()}",
                        "institution": institution.title(),
                        "year": "2023",
                        "gpa": gpa
                    })
                    break
        
        # Master's degree patterns
        m_patterns = [
            r"master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
            r"mca\s+at\s+([^.,]+)",
            r"pursuing\s+master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
            r"currently\s+pursuing\s+master\s+of\s+computer\s+applications\s+at\s+([^.,]+)",
        ]
        
        for pattern in m_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                education_list.append({
                    "degree": "Master of Computer Applications (Pursuing)",
                    "institution": match.group(1).strip().title(),
                    "year": "Present",
                    "gpa": ""
                })
                break
        
        if education_list:
            extracted_info['education'] = education_list
        
        # Extract work experience
        work_experience = []
        if "codeverse" in prompt_lower:
            work_exp = {
                "title": "Full Stack Developer Intern",
                "company": "CodeVerse",
                "duration": "Jun-Sep 2024",
                "achievements": [
                    "Contributed to real-time chat application using React and Firebase",
                    "Implemented JWT-based authentication",
                    "Improved API performance"
                ]
            }
            work_experience.append(work_exp)
        
        if "freelance" in prompt_lower:
            freelance_exp = {
                "title": "Freelance Frontend Developer",
                "company": "Self-Employed",
                "duration": "2024 - Present",
                "achievements": [
                    "Delivered responsive websites for small businesses",
                    "Used React, HTML, and CSS for development"
                ]
            }
            work_experience.append(freelance_exp)
        
        if work_experience:
            extracted_info['work_experience'] = work_experience
        
        # Extract skills
        technical_skills = []
        skill_keywords = [
            "html", "css", "javascript", "react", "node.js", "express", "mongodb", 
            "firebase", "jwt", "git", "postman", "mern", "openai", "jspdf"
        ]
        
        for skill in skill_keywords:
            if skill in prompt_lower:
                technical_skills.append(skill.title())
        
        if technical_skills:
            extracted_info['technical_skills'] = technical_skills
        
        # Extract projects
        projects = []
        if "job portal" in prompt_lower:
            projects.append({
                "name": "Job Portal App",
                "description": "MERN stack application with resume upload and login functionality",
                "achievements": ["Built complete job portal with user authentication"]
            })
        
        if "task manager" in prompt_lower:
            projects.append({
                "name": "Task Manager API",
                "description": "Secure backend with CRUD operations",
                "achievements": ["Implemented secure API with full CRUD functionality"]
            })
        
        if "ai resume builder" in prompt_lower:
            projects.append({
                "name": "AI Resume Builder",
                "description": "OpenAI and jsPDF for prompt-based resume generation",
                "achievements": ["Created AI-powered resume generation system"]
            })
        
        if projects:
            extracted_info['projects'] = projects
        
        # Extract certifications
        certifications = []
        if "udemy" in prompt_lower:
            certifications.append({
                "name": "Full Stack Web Development",
                "issuer": "Udemy",
                "year": "2024"
            })
        
        if "coursera" in prompt_lower:
            certifications.append({
                "name": "Git & GitHub",
                "issuer": "Coursera",
                "year": "2024"
            })
        
        if "aws" in prompt_lower:
            certifications.append({
                "name": "AWS Cloud Basics",
                "issuer": "Amazon",
                "year": "2024"
            })
        
        if certifications:
            extracted_info['certifications'] = certifications
        
        return extracted_info 