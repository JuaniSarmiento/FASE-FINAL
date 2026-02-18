from abc import ABC, abstractmethod
from typing import Any

class UnitOfWork(ABC):
    """
    Abstract interface for Unit of Work pattern.
    Manages transactions across repositories.
    """
    
    @abstractmethod
    def __enter__(self) -> 'UnitOfWork':
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
