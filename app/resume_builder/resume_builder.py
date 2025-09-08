import os
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.resume_builder.gemini_integration import GeminiResumeGenerator
from app.resume_builder.pdf_generator import ResumePDFGenerator
from app.resume_builder.models import GeneratedResume

class ResumeBuilder:
    def __init__(self):
        self.gemini_generator = GeminiResumeGenerator()
        self.pdf_generator = ResumePDFGenerator()
    
    def create_resume(self, user_id: int, resume_name: str, user_prompt: str, 
                     user_data: Dict[str, Any], template_name: str = "professional", 
                     db: Session = None) -> Dict[str, Any]:
        """
        Create a complete AI-generated resume
        """
        try:
            # Step 1: Generate content using Gemini AI
            print(f"Generating resume content for user {user_id}...")
            resume_content = self.gemini_generator.generate_resume_content(user_prompt, user_data)
            
            # Step 2: Save to database (no PDF generation yet)
            if db:
                generated_resume = GeneratedResume(
                    user_id=user_id,
                    resume_name=resume_name,
                    prompt_text=user_prompt,
                    generated_content=json.dumps(resume_content),
                    template_used=template_name,
                    pdf_filename=None,  # No PDF file stored
                    created_at=datetime.now(),
                    is_active=True
                )
                
                db.add(generated_resume)
                db.commit()
                db.refresh(generated_resume)
                
                resume_id = generated_resume.id
            else:
                resume_id = None
            
            return {
                "success": True,
                "resume_id": resume_id,
                "content": resume_content,
                "message": "Resume generated successfully!"
            }
            
        except Exception as e:
            print(f"Error creating resume: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate resume. Please try again."
            }
    
    def get_user_resumes(self, user_id: int, db: Session) -> list:
        """
        Get all resumes for a specific user
        """
        try:
            resumes = db.query(GeneratedResume).filter(
                GeneratedResume.user_id == user_id,
                GeneratedResume.is_active == True
            ).order_by(GeneratedResume.created_at.desc()).all()
            
            return [
                {
                    "id": resume.id,
                    "name": resume.resume_name,
                    "template": resume.template_used,
                    "created_at": resume.created_at.strftime("%Y-%m-%d %H:%M"),
                    "content": json.loads(resume.generated_content) if resume.generated_content else None
                }
                for resume in resumes
            ]
        except Exception as e:
            print(f"Error fetching user resumes: {e}")
            return []
    
    def get_resume_by_id(self, resume_id: int, user_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get a specific resume by ID
        """
        try:
            resume = db.query(GeneratedResume).filter(
                GeneratedResume.id == resume_id,
                GeneratedResume.user_id == user_id,
                GeneratedResume.is_active == True
            ).first()
            
            if resume:
                return {
                    "id": resume.id,
                    "name": resume.resume_name,
                    "template": resume.template_used,
                    "created_at": resume.created_at.strftime("%Y-%m-%d %H:%M"),
                    "content": json.loads(resume.generated_content) if resume.generated_content else None,
                    "prompt": resume.prompt_text
                }
            return None
        except Exception as e:
            print(f"Error fetching resume by ID: {e}")
            return None
    
    def delete_resume(self, resume_id: int, user_id: int, db: Session) -> bool:
        """
        Delete a resume (soft delete)
        """
        try:
            resume = db.query(GeneratedResume).filter(
                GeneratedResume.id == resume_id,
                GeneratedResume.user_id == user_id
            ).first()
            
            if resume:
                # Soft delete
                resume.is_active = False
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting resume: {e}")
            return False
    
    def regenerate_resume(self, resume_id: int, user_id: int, new_prompt: str, 
                         user_data: Dict[str, Any], template_name: str, db: Session) -> Dict[str, Any]:
        """
        Regenerate a resume with new prompt
        """
        try:
            # Get the original resume
            original_resume = db.query(GeneratedResume).filter(
                GeneratedResume.id == resume_id,
                GeneratedResume.user_id == user_id
            ).first()
            
            if not original_resume:
                return {
                    "success": False,
                    "message": "Resume not found"
                }
            
            # Generate new content
            resume_content = self.gemini_generator.generate_resume_content(new_prompt, user_data)
            
            # Update database (no PDF generation)
            original_resume.prompt_text = new_prompt
            original_resume.generated_content = json.dumps(resume_content)
            original_resume.template_used = template_name
            original_resume.pdf_filename = None  # No PDF file stored
            original_resume.created_at = datetime.now()
            
            db.commit()
            
            return {
                "success": True,
                "content": resume_content,
                "message": "Resume regenerated successfully!"
            }
            
        except Exception as e:
            print(f"Error regenerating resume: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to regenerate resume. Please try again."
            }
    
    def get_available_templates(self) -> list:
        """
        Get list of available resume templates
        """
        return [
            {
                "id": "professional",
                "name": "Professional",
                "description": "Clean, traditional design optimized for ATS systems",
                "preview": "professional_preview.png"
            }
        ] 