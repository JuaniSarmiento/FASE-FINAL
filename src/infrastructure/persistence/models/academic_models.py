from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base

class SubjectModel(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    courses = relationship("CourseModel", back_populates="subject")

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("SubjectModel", back_populates="courses")
    enrollments = relationship("EnrollmentModel", back_populates="course")

class EnrollmentModel(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    module_id = Column(String, nullable=True) # Linked to activities.id (type=module)
    status = Column(String, default="active") # active, completed, dropped
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("CourseModel", back_populates="enrollments")
    # student = relationship("UserModel") # Assuming UserModel is in same metadata, but avoiding circular import unless necessary.
