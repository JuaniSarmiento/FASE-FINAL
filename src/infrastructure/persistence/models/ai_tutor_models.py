import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Float, Boolean, Text
from sqlalchemy.orm import relationship
from ..database import Base

# TutorSessionModel removed in favor of SessionModel in learning_models.py

class TutorMessageModel(Base):
    __tablename__ = "tutor_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False) # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionModel", back_populates="messages")

class CognitiveTraceModel(Base):
    __tablename__ = "cognitive_traces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    inferred_state = Column(String, nullable=True) # e.g. "confused", "flow"
    confidence = Column(Float, default=0.0)
    detected_at = Column(DateTime, default=datetime.utcnow)

    # session = relationship("SessionModel", back_populates="cognitive_traces") 
    # SessionModel needs to add cognitive_traces relationship if we want bi-directional.
    # For now, leaving it uni-directional or mapped if SessionModel is updated.
