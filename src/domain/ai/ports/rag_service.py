from abc import ABC, abstractmethod
from typing import List, Any
from src.domain.learning.ports.document_repository import ActivityDocument

class RagServicePort(ABC):
    @abstractmethod
    def process_document(self, activity_id: str, file_path: str, filename: str) -> ActivityDocument:
        """
        Processes a document for RAG: loads, chunks, embeds, and stores.
        """
        pass

    @abstractmethod
    def query(self, activity_id: str, query_text: str, n_results: int = 3) -> List[str]:
        """
        Retrieves relevant document chunks for a query.
        """
        pass
        
    @abstractmethod
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer using the LLM based on the provided context.
        """
        pass

    @abstractmethod
    def generate_tutor_response(self, query: str, context: str, history: List[dict], code_context: str = None) -> str:
        """
        Generates a response acting as a tutor, using context, history, and code.
        """
        pass
