from src.domain.analytics.entities.risk_analysis import RiskAnalysis
from src.domain.analytics.ports.analytics_repository import AnalyticsRepository
from src.application.shared.unit_of_work import UnitOfWork
from src.application.analytics.dtos.analytics_dtos import CreateRiskAnalysisRequest, RiskAnalysisDTO
import random

class GenerateRiskAnalysis:
    def __init__(self, analytics_repository: AnalyticsRepository, uow: UnitOfWork):
        self.analytics_repository = analytics_repository
        self.uow = uow

    def execute(self, request: CreateRiskAnalysisRequest) -> RiskAnalysisDTO:
        # Mock logic for risk calculation:
        # In a real scenario, this would aggregate data from Grading, Attendance, etc.
        score = round(random.uniform(0.1, 0.9), 2)
        factors = []
        if score > 0.7:
            factors.append("Low engagement")
            factors.append("Late submissions")
        elif score > 0.4:
             factors.append("Irregular login")
        
        analysis = RiskAnalysis.create(
            student_id=request.student_id,
            risk_score=score,
            risk_factors=factors,
            details={"automated_reason": "Simulated analysis based on MVP constraints."}
        )
        
        with self.uow:
            self.analytics_repository.save(analysis)
            
        return RiskAnalysisDTO(
            id=analysis.id,
            student_id=analysis.student_id,
            risk_score=analysis.risk_score,
            risk_factors=analysis.risk_factors,
            details=analysis.details,
            created_at=analysis.created_at
        )
