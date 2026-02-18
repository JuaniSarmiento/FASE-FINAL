from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ActivityDocument:
    id: str
    activity_id: str
    filename: str
    content_text: Optional[str] = None
    embedding_id: Optional[str] = None
    created_at: datetime = datetime.now()

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: ActivityDocument) -> None:
        pass

    @abstractmethod
    def find_by_activity(self, activity_id: str) -> List[ActivityDocument]:
        pass
        
    @abstractmethod
    def find_by_id(self, document_id: str) -> Optional[ActivityDocument]:
        pass
