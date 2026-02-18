from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.learning.ports.document_repository import DocumentRepository, ActivityDocument
from src.infrastructure.persistence.models.learning_models import ActivityDocumentModel

class SqlAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, document: ActivityDocument) -> None:
        model = self.session.query(ActivityDocumentModel).filter_by(id=document.id).first()
        if not model:
            model = ActivityDocumentModel(
                id=document.id,
                activity_id=document.activity_id,
                filename=document.filename,
                content_text=document.content_text,
                embedding_id=document.embedding_id,
                created_at=document.created_at
            )
            self.session.add(model)
        else:
            model.filename = document.filename
            model.content_text = document.content_text
            model.embedding_id = document.embedding_id

    def find_by_activity(self, activity_id: str) -> List[ActivityDocument]:
        models = self.session.query(ActivityDocumentModel).filter_by(activity_id=activity_id).all()
        return [
            ActivityDocument(
                id=m.id,
                activity_id=m.activity_id,
                filename=m.filename,
                content_text=m.content_text,
                embedding_id=m.embedding_id,
                created_at=m.created_at
            ) for m in models
        ]

    def find_by_id(self, document_id: str) -> Optional[ActivityDocument]:
        model = self.session.query(ActivityDocumentModel).filter_by(id=document_id).first()
        if not model:
            return None
        return ActivityDocument(
            id=model.id,
            activity_id=model.activity_id,
            filename=model.filename,
            content_text=model.content_text,
            embedding_id=model.embedding_id,
            created_at=model.created_at
        )
