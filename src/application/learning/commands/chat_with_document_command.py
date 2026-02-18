from src.domain.ai.ports.rag_service import RagServicePort

class ChatWithDocumentCommand:
    def __init__(self, rag_service: RagServicePort):
        self.rag_service = rag_service

    def execute(self, activity_id: str, query: str) -> str:
        # 1. Retrieve context
        context_docs = self.rag_service.query(activity_id, query)
        context_text = "\n\n".join(context_docs)
        
        if not context_text:
            return "I couldn't find relevant information in the documents."

        # 2. Generate Answer (using Ollama)
        # I'll implement a helper in RagService to call Ollama for chat
        return self.rag_service.generate_answer(query, context_text)
