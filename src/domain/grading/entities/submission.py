from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.domain.shared.entity import AggregateRoot
from ..value_objects.submission_status import SubmissionStatus
from ..value_objects.score import Score
from .exercise_attempt import ExerciseAttempt

@dataclass(kw_only=True)
class Submission(AggregateRoot):
    activity_id: str
    student_id: str
    status: SubmissionStatus = SubmissionStatus.PENDING
    score: Optional[Score] = None
    attempts: List[ExerciseAttempt] = field(default_factory=list)
    submitted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_attempt(self, attempt: ExerciseAttempt) -> None:
        self.attempts.append(attempt)
        self.updated_at = datetime.now()
        
    def submit(self) -> None:
        self.status = SubmissionStatus.SUBMITTED
        self.submitted_at = datetime.now()
        self.updated_at = datetime.now()
        
    def grade(self, score: Score) -> None:
        self.score = score
        self.status = SubmissionStatus.GRADED
        self.updated_at = datetime.now()
