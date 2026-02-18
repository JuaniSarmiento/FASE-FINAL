from src.domain.shared.exceptions import DomainException

class GradingException(DomainException):
    """Base exception for grading context."""
    pass

class AlreadyGradedException(GradingException):
    """Raised when trying to grade an already graded submission."""
    pass

class SubmissionNotFoundException(GradingException):
    """Raised when submission is not found."""
    pass
