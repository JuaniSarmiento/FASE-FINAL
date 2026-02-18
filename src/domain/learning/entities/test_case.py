from dataclasses import dataclass
from typing import Optional
from src.domain.shared.entity import Entity

@dataclass(kw_only=True)
class TestCase(Entity):
    input_data: str
    expected_output: str
    is_hidden: bool = False
    weight: float = 1.0
