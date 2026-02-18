from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from src.application.learning.commands.upload_document_command import UploadDocumentCommand
from src.application.learning.commands.chat_with_document_command import ChatWithDocumentCommand
from src.infrastructure.http.dependencies.container import get_upload_document_command, get_chat_with_document_command
from src.application.learning.dtos.rag_dtos import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/activities/{activity_id}/document")
def upload_document(
    activity_id: str,
    file: UploadFile = File(...),
    command: UploadDocumentCommand = Depends(get_upload_document_command)
):
    try:
        # Decoupling: Unpack UploadFile here in the Infrastructure layer
        # command expects a file-like object and a filename
        message = command.execute(activity_id, file.file, file.filename)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activities/{activity_id}/chat", response_model=ChatResponse)
def chat_with_document(
    activity_id: str,
    request: ChatRequest,
    command: ChatWithDocumentCommand = Depends(get_chat_with_document_command)
):
    try:
        response = command.execute(activity_id, request.query)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
