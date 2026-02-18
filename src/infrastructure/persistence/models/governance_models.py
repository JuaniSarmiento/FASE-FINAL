from sqlalchemy import Column, String, DateTime, Text, Enum as SqlEnum
from datetime import datetime
import uuid
from ..database import Base

class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, nullable=False, index=True)
    incident_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, default="low")
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, default="")
