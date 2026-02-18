from sqlalchemy import Column, String, Boolean, DateTime, ARRAY
from datetime import datetime
import uuid
from ..database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True) # Optional as per legacy likely
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    roles = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
