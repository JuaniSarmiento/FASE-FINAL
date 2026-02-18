from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.analytics_repository_impl import SqlAlchemyAnalyticsRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.analytics.commands.generate_risk_analysis import GenerateRiskAnalysis
from src.application.analytics.dtos.analytics_dtos import CreateRiskAnalysisRequest, RiskAnalysisDTO

router = APIRouter()

def get_analytics_repository(db: Session = Depends(get_db)):
    return SqlAlchemyAnalyticsRepository(db)

def get_unit_of_work(db: Session = Depends(get_db)):
    return SqlAlchemyUnitOfWork(lambda: db)

@router.post("/risk-analysis/{student_id}", response_model=RiskAnalysisDTO, status_code=status.HTTP_201_CREATED)
def generate_risk_analysis(
    student_id: str,
    repo: SqlAlchemyAnalyticsRepository = Depends(get_analytics_repository),
    uow = Depends(get_unit_of_work)
):
    request = CreateRiskAnalysisRequest(student_id=student_id)
    command = GenerateRiskAnalysis(repo, uow)
    try:
        return command.execute(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
