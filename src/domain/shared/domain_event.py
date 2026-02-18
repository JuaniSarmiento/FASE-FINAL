from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    """Base class for all Domain Events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)
