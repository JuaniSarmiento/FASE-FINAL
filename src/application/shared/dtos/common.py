from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, List, Any

T = TypeVar('T')

@dataclass
class DTO:
    """Base class for Data Transfer Objects."""
    pass

@dataclass
class Result(Generic[T]):
    """Generic result wrapper for application layer responses."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, data: T) -> 'Result[T]':
        return cls(success=True, data=data)
    
    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        return cls(success=False, error=error)
