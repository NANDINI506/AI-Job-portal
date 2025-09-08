from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Import GeneratedResume to ensure it's available for relationships
from .resume_builder.models import GeneratedResume

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_supervisor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    resume_filename = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    education = Column(String, nullable=True)
    skills = Column(String, nullable=True)  # Comma-separated skills
    resume_email = Column(String, nullable=True)
    resume_phone = Column(String, nullable=True)
    applications = relationship("Application", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    generated_resumes = relationship("GeneratedResume", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    salary = Column(Float, default=0.0)
    skills = Column(String)
    job_url = Column(String, nullable=True)  # Store original job URL for "Read More"
    experience_level = Column(String, default="Mid-Senior")  # Entry-level, Mid-level, Senior, etc.
    job_type = Column(String, default="Full-time")  # Full-time, Part-time, Contract, etc.
    remote_policy = Column(String, default="On-site")  # On-site, Remote, Hybrid
    posted_by = Column(String, default="System")
    posted_date = Column(DateTime, default=datetime.now)
    
    # Add unique constraint to prevent exact duplicates
    __table_args__ = (
        UniqueConstraint('title', 'company', 'location', name='unique_job'),
    )
    
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    cover_letter = Column(String)
    application_date = Column(DateTime, default=datetime.now)
    status = Column(String, default="Unviewed")
    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="job_alert")  # job_alert, system, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    related_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    
    user = relationship("User", back_populates="notifications")
