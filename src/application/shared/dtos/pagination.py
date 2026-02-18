from dataclasses import dataclass
from typing import TypeVar, Generic, List
from .common import DTO

T = TypeVar('T')

@dataclass
class PaginationRequest(DTO):
    page: int = 1
    page_size: int = 20

@dataclass
class PagedResult(Generic[T], DTO):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
