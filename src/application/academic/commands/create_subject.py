from typing import Optional
from src.domain.academic.entities.subject import Subject
from src.domain.academic.ports.academic_repository import SubjectRepository
from src.application.shared.unit_of_work import UnitOfWork
from src.application.academic.dtos.academic_dtos import CreateSubjectRequest, SubjectDTO

class CreateSubject:
    def __init__(self, subject_repository: SubjectRepository, uow: UnitOfWork):
        self.subject_repository = subject_repository
        self.uow = uow

    def execute(self, request: CreateSubjectRequest) -> SubjectDTO:
        # Business logic: validate code uniqueness? (Optional for MVP)
        
        subject = Subject.create(
            name=request.name,
            code=request.code,
            description=request.description
        )
        
        with self.uow:
            self.subject_repository.save(subject)
            self.uow.commit() # Optimistic commit or let usage decide?
            # Usually UoW context manager commits on exit if no error.
            # But specific implementation might need manual commit.
            # In my current UoW (sqlalchemy), it commits on exit.
            
        return SubjectDTO(
            id=subject.id,
            name=subject.name,
            code=subject.code
        )
