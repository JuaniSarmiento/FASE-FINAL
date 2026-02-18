from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject:
    """Base class for all Value Objects. Must be immutable."""
    pass
