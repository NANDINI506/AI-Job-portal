from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class GeneratedResume(Base):
    __tablename__ = "generated_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_name = Column(String(255), nullable=False)
    prompt_text = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    template_used = Column(String(100), default="modern")
    pdf_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationship to User
    user = relationship("User", back_populates="generated_resumes") 