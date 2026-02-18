from typing import List, Optional
import json
from sqlalchemy.orm import Session
from src.domain.analytics.ports.analytics_repository import AnalyticsRepository
from src.domain.analytics.entities.risk_analysis import RiskAnalysis
from src.infrastructure.persistence.models.grading_models import RiskAnalysisModel

class SqlAlchemyAnalyticsRepository(AnalyticsRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, analysis: RiskAnalysis) -> None:
        # Check if exists to update
        existing = self.db.query(RiskAnalysisModel).filter_by(submission_id=analysis.submission_id).first()
        if existing:
             self.db.delete(existing)
             
        model = RiskAnalysisModel(
            id=analysis.id,
            submission_id=analysis.submission_id,
            risk_score=analysis.risk_score,
            risk_level=analysis.risk_level,
            diagnosis=analysis.diagnosis,
            evidence=json.dumps(analysis.evidence),
            teacher_advice=analysis.teacher_advice,
            positive_aspects=json.dumps(analysis.positive_aspects),
            analyzed_at=analysis.analyzed_at
        )
        self.db.add(model)

    def find_latest_by_student(self, student_id: str) -> Optional[RiskAnalysis]:
        # This lookup is more complex now because RiskAnalysis depends on Submission which depends on Student
        # For simplicity in this fix, we might need to join tables or just return None if not strictly needed immediately
        # But let's try to do it right: Join RiskAnalysis -> Submission -> filter by student_id
        from src.infrastructure.persistence.models.grading_models import SubmissionModel
        
        model = (
            self.db.query(RiskAnalysisModel)
            .join(SubmissionModel)
            .filter(SubmissionModel.student_id == student_id)
            .order_by(RiskAnalysisModel.analyzed_at.desc())
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def list_by_student(self, student_id: str) -> List[RiskAnalysis]:
        from src.infrastructure.persistence.models.grading_models import SubmissionModel
        
        models = (
            self.db.query(RiskAnalysisModel)
            .join(SubmissionModel)
            .filter(SubmissionModel.student_id == student_id)
            .order_by(RiskAnalysisModel.analyzed_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]
        
    def _to_entity(self, model: RiskAnalysisModel) -> RiskAnalysis:
        evidence = []
        positive_aspects = []
        try:
             evidence = json.loads(model.evidence) if model.evidence else []
             positive_aspects = json.loads(model.positive_aspects) if model.positive_aspects else []
        except:
             pass
             
        return RiskAnalysis(
            id=model.id,
            submission_id=model.submission_id,
            risk_score=model.risk_score,
            risk_level=model.risk_level,
            diagnosis=model.diagnosis,
            evidence=evidence,
            teacher_advice=model.teacher_advice,
            positive_aspects=positive_aspects,
            analyzed_at=model.analyzed_at
        )
