from dataclasses import dataclass, field
from typing import List, Dict
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class Schedule(ValueObject):
    # e.g., {"Monday": ["10:00-12:00"], "Wednesday": ["14:00-16:00"]}
    time_slots: Dict[str, List[str]] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return str(self.time_slots)
