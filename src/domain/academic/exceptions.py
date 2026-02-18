from src.domain.shared.exceptions import DomainException

class AcademicException(DomainException):
    """Base exception for academic context."""
    pass

class EnrollmentClosedException(AcademicException):
    """Raised when trying to enroll in a closed course/commission."""
    pass

class InvalidAccessCodeException(AcademicException):
    """Raised when access code is invalid."""
    pass

class DuplicateEnrollmentException(AcademicException):
    """Raised when student is already enrolled."""
    pass
