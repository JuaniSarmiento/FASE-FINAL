from dataclasses import dataclass, field
from typing import Any, List
import uuid

@dataclass
class Entity:
    """Base class for all Domain Entities."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False
        
    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class AggregateRoot(Entity):
    """Base class for Aggregate Roots that can raise Domain Events."""
    _domain_events: List[Any] = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to the aggregate."""
        self._domain_events.append(event)
        
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
        
    @property
    def domain_events(self) -> List[Any]:
        """Get pending domain events."""
        return list(self._domain_events)
