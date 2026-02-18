import os
import shutil
from typing import BinaryIO
from src.domain.ai.ports.rag_service import RagServicePort

class UploadDocumentCommand:
    def __init__(self, rag_service: RagServicePort):
        self.rag_service = rag_service
        self.upload_dir = "./uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def execute(self, activity_id: str, file_obj: BinaryIO, filename: str) -> str:
        file_path = os.path.join(self.upload_dir, f"{activity_id}_{filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
            
        # Process for RAG
        self.rag_service.process_document(activity_id, file_path, filename)
        
        # Cleanup file? Maybe keep it.
        return "Document processed successfully"
