from enum import Enum

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"
    REJECTED = "rejected"
