from src.domain.shared.exceptions import DomainException

class TutorException(DomainException):
    """Base exception for AI tutor context."""
    pass

class SessionExpiredException(TutorException):
    """Raised when a tutor session has expired."""
    pass

class InvalidSessionStateException(TutorException):
    """Raised when session state transition is invalid."""
    pass
