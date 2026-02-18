from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.incident_repository_impl import SqlAlchemyIncidentRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.governance.commands.report_incident import ReportIncident
from src.application.governance.dtos.governance_dtos import ReportIncidentRequest, IncidentDTO

router = APIRouter()

def get_incident_repository(db: Session = Depends(get_db)):
    return SqlAlchemyIncidentRepository(db)

def get_unit_of_work(db: Session = Depends(get_db)):
    return SqlAlchemyUnitOfWork(lambda: db)

@router.post("/incidents", response_model=IncidentDTO, status_code=status.HTTP_201_CREATED)
def report_incident(
    request: ReportIncidentRequest,
    repo: SqlAlchemyIncidentRepository = Depends(get_incident_repository),
    uow = Depends(get_unit_of_work)
):
    command = ReportIncident(repo, uow)
    try:
        return command.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents", response_model=List[IncidentDTO])
def list_incidents(
    repo: SqlAlchemyIncidentRepository = Depends(get_incident_repository)
):
    incidents = repo.list_all()
    return [
        IncidentDTO(
            id=inc.id,
            student_id=inc.student_id,
            incident_type=inc.incident_type.value,
            description=inc.description,
            severity=inc.severity.value,
            status=inc.status.value,
            created_at=inc.created_at,
            resolved_at=inc.resolved_at,
            resolution_notes=inc.resolution_notes
        )
        for inc in incidents
    ]
