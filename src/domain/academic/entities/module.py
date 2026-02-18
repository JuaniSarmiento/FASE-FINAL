from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.domain.shared.entity import Entity

@dataclass
class Module(Entity):
    course_id: str
    title: str
    order: int
    description: Optional[str] = None
    parent_module_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_order(self, new_order: int) -> None:
        self.order = new_order
        self.updated_at = datetime.now()
