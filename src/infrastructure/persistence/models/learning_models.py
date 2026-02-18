import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..database import Base
from ....domain.learning.value_objects.difficulty import Difficulty
from ....domain.learning.value_objects.programming_language import ProgrammingLanguage
from ....domain.learning.value_objects.exercise_status import ExerciseStatus

class ActivityModel(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String, nullable=False, index=True)
    teacher_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    status = Column(String, default="draft")
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercises = relationship("ExerciseModel", back_populates="activity")

class ExerciseModel(Base):
    __tablename__ = "exercises"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    title = Column(String, nullable=False)
    problem_statement = Column(String, nullable=False)
    starter_code = Column(String, nullable=False)
    solution_code = Column(String, nullable=True) # AI Generated Solution for Grading
    # Storing Enums as Strings in DB for simplicity and portability
    difficulty = Column(String, nullable=False) 
    language = Column(String, nullable=False)
    status = Column(String, default=ExerciseStatus.DRAFT.value)
    test_cases_json = Column(String, nullable=True) # Storing test cases as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("ActivityModel", back_populates="exercises")

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, nullable=False, index=True)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    status = Column(String, default="active")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relation to messages
    messages = relationship("TutorMessageModel", back_populates="session")



class ActivityDocumentModel(Base):
    __tablename__ = "activity_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_text = Column(String, nullable=True) # Using String/Text for small content, or large text
    embedding_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

