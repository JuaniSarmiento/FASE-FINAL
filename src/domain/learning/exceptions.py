from src.domain.shared.exceptions import DomainException

class LearningException(DomainException):
    """Base exception for learning context."""
    pass

class ActivityNotFoundException(LearningException):
    """Raised when an activity is not found."""
    pass

class ExerciseInvalidException(LearningException):
    """Raised when an exercise is invalid."""
    pass
