import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from ..database import Base
from ....domain.grading.value_objects.submission_status import SubmissionStatus

class SubmissionModel(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, nullable=False, index=True) # FK to User usually
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    status = Column(String, default=SubmissionStatus.PENDING.value)
    final_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attempts = relationship("ExerciseAttemptModel", back_populates="submission", cascade="all, delete-orphan")
    risk_analysis = relationship("RiskAnalysisModel", uselist=False, back_populates="submission", cascade="all, delete-orphan") # One-to-One

class ExerciseAttemptModel(Base):
    __tablename__ = "exercise_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False)
    exercise_id = Column(String, ForeignKey("exercises.id"), nullable=False)
    code_submitted = Column(Text, nullable=False)
    is_passing = Column(Boolean, default=False)
    grade = Column(Float, nullable=True) # New field to store specific grade (0-10 or 0-100)
    execution_output = Column(Text, nullable=True) # stdout/stderr combined or JSON
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("SubmissionModel", back_populates="attempts")

class RiskAnalysisModel(Base):
    __tablename__ = "risk_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False, unique=True)
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False)    # LOW, MEDIUM, HIGH, CRITICAL
    diagnosis = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)         # JSON 
    teacher_advice = Column(Text, nullable=True)
    positive_aspects = Column(JSON, nullable=True) # JSON 
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    submission = relationship("SubmissionModel", back_populates="risk_analysis")
