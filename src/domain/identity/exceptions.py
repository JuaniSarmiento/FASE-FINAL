from src.domain.shared.exceptions import DomainException

class IdentityException(DomainException):
    """Base exception for identity context."""
    pass

class InvalidCredentialsException(IdentityException):
    """Raised when credentials are invalid."""
    pass

class UserNotFoundException(IdentityException):
    """Raised when a user is not found."""
    pass

class EmailAlreadyExistsException(IdentityException):
    """Raised when registering an email that already exists."""
    pass
