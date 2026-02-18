import sys
import os
sys.path.append(os.getcwd())

print("Checking imports...")

try:
    print("1. Importing RagServicePort...")
    from src.domain.ai.ports.rag_service import RagServicePort
    
    print("2. Importing RagService (Implementation)...")
    from src.infrastructure.ai.rag.rag_service import RagService
    
    print("3. Importing ChatWithDocumentCommand...")
    from src.application.learning.commands.chat_with_document_command import ChatWithDocumentCommand
    
    print("4. Importing UploadDocumentCommand...")
    from src.application.learning.commands.upload_document_command import UploadDocumentCommand
    
    print("5. Importing RagRouter...")
    from src.infrastructure.http.routers.learning.rag_router import router
    
    print("✅ All imports successful. Architecture refactor seems valid.")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
