from dataclasses import dataclass
from src.domain.shared.entity import Entity

@dataclass(kw_only=True)
class Subject(Entity):
    name: str
    code: str
    description: str = ""

    @classmethod
    def create(cls, name: str, code: str, description: str = "") -> 'Subject':
        return cls(name=name, code=code, description=description)
