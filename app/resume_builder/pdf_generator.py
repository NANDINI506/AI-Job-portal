from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from typing import Dict, Any, List
from datetime import datetime

class ResumePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_professional_styles()
    
    def _setup_professional_styles(self):
        """Setup professional paragraph styles for resume"""
        
        # Professional header style
        self.header_style = ParagraphStyle(
            'ProfessionalHeader',
            parent=self.styles['Heading1'],
            fontSize=22,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0
        )
        
        # Job title style
        self.job_title_style = ParagraphStyle(
            'JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=2,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        # Company style
        self.company_style = ParagraphStyle(
            'Company',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'NormalText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica'
        )
        
        # Bullet point style
        self.bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=2,
            leftIndent=15,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica'
        )
        
        # Contact info style
        self.contact_style = ParagraphStyle(
            'ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )
    
    def generate_pdf(self, resume_data: Dict[str, Any], template_name: str = "professional", output_path: str = None) -> str:
        """
        Generate a professional PDF resume from the provided data
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Get resumes directory from environment variable
            resumes_dir = os.environ.get('RESUMES_DIR', 'resumes')
            output_path = os.path.join(resumes_dir, f"ai_resume_{timestamp}.pdf")
        
        # Ensure the resumes directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Build the story (content)
        story = self._build_professional_resume(resume_data)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_professional_resume(self, resume_data: Dict[str, Any]) -> List:
        """Build professional resume content"""
        story = []
        
        # Header with personal info
        personal_info = resume_data.get('personal_info', {})
        name = personal_info.get('name', 'Professional Candidate')
        
        # Name header
        story.append(Paragraph(name.upper(), self.header_style))
        story.append(Spacer(1, 4))
        
        # Contact information
        contact_info = []
        if personal_info.get('email'):
            contact_info.append(personal_info['email'])
        if personal_info.get('phone'):
            contact_info.append(personal_info['phone'])
        if personal_info.get('location'):
            contact_info.append(personal_info['location'])
        if personal_info.get('linkedin'):
            contact_info.append(personal_info['linkedin'])
        
        if contact_info:
            contact_text = " | ".join(contact_info)
            story.append(Paragraph(contact_text, self.contact_style))
            story.append(Spacer(1, 12))
        
        # Professional Summary
        if resume_data.get('professional_summary'):
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            story.append(Paragraph(resume_data['professional_summary'], self.normal_style))
            story.append(Spacer(1, 8))
        
        # Work Experience
        if resume_data.get('work_experience'):
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            
            for job in resume_data['work_experience']:
                # Job title and company
                job_title = job.get('title', '')
                company = job.get('company', '')
                duration = job.get('duration', '')
                
                title_company = f"{job_title} | {company}"
                if duration:
                    title_company += f" | {duration}"
                
                story.append(Paragraph(title_company, self.job_title_style))
                
                # Achievements
                achievements = job.get('achievements', [])
                for achievement in achievements:
                    bullet_text = f"• {achievement}"
                    story.append(Paragraph(bullet_text, self.bullet_style))
                
                story.append(Spacer(1, 6))
        
        # Skills
        if resume_data.get('skills'):
            story.append(Paragraph("TECHNICAL SKILLS", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            
            skills = resume_data['skills']
            skills_text = ""
            
            if skills.get('technical_skills'):
                skills_text += f"<b>Technical Skills:</b> {', '.join(skills['technical_skills'])}<br/>"
            if skills.get('soft_skills'):
                skills_text += f"<b>Soft Skills:</b> {', '.join(skills['soft_skills'])}<br/>"
            if skills.get('tools'):
                skills_text += f"<b>Tools & Technologies:</b> {', '.join(skills['tools'])}"
            
            if skills_text:
                story.append(Paragraph(skills_text, self.normal_style))
                story.append(Spacer(1, 8))
        
        # Projects
        if resume_data.get('projects'):
            story.append(Paragraph("KEY PROJECTS", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            
            for project in resume_data['projects']:
                project_name = project.get('name', '')
                description = project.get('description', '')
                
                story.append(Paragraph(f"<b>{project_name}</b>", self.job_title_style))
                story.append(Paragraph(description, self.normal_style))
                
                achievements = project.get('achievements', [])
                for achievement in achievements:
                    bullet_text = f"• {achievement}"
                    story.append(Paragraph(bullet_text, self.bullet_style))
                
                story.append(Spacer(1, 6))
        
        # Education
        if resume_data.get('education'):
            story.append(Paragraph("EDUCATION", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            
            for edu in resume_data['education']:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                gpa = edu.get('gpa', '')
                
                edu_text = f"{degree} | {institution}"
                if year:
                    edu_text += f" | {year}"
                if gpa:
                    edu_text += f" | GPA: {gpa}"
                
                story.append(Paragraph(edu_text, self.normal_style))
                story.append(Spacer(1, 3))
        
        # Certifications
        if resume_data.get('certifications'):
            story.append(Paragraph("CERTIFICATIONS", self.section_style))
            story.append(Paragraph("_" * 60, self.normal_style))
            
            for cert in resume_data['certifications']:
                cert_name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                year = cert.get('year', '')
                
                cert_text = f"{cert_name} | {issuer}"
                if year:
                    cert_text += f" | {year}"
                
                story.append(Paragraph(cert_text, self.normal_style))
                story.append(Spacer(1, 3))
        
        return story
    
    def make_pdf_readonly(self, pdf_path: str) -> bool:
        """
        Make the PDF read-only (non-editable)
        Note: This is a basic implementation. For production, you might want to use
        more advanced PDF security features.
        """
        try:
            # This is a placeholder for PDF security
            # In a production environment, you would use PyPDF2 or similar to add security
            return True
        except Exception as e:
            print(f"Error making PDF readonly: {e}")
            return False 