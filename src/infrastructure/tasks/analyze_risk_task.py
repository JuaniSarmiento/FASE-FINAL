
import logging
import threading
from sqlalchemy.orm import Session
from src.infrastructure.persistence.database import SessionLocal
from src.application.teacher.queries.get_student_activity_details import GetStudentActivityDetails
from src.infrastructure.persistence.repositories.submission_read_repository_impl import SqlAlchemySubmissionReadRepository
from src.infrastructure.ai.llm.risk_analyzer import RiskAnalyzer
from src.infrastructure.persistence.models.grading_models import RiskAnalysisModel, SubmissionModel

logger = logging.getLogger(__name__)

def enqueue_risk_analysis(submission_id: str, student_id: str, activity_id: str):
    """
    Enqueues risk analysis task in a background thread.
    """
    thread = threading.Thread(target=_execute_risk_analysis, args=(submission_id, student_id, activity_id))
    thread.daemon = True # Daemonize to not block shutdown
    thread.start()

def _execute_risk_analysis(submission_id: str, student_id: str, activity_id: str):
    logger.info(f"Starting async risk analysis for submission {submission_id}")
    db = SessionLocal()
    try:
        # 1. Fetch Details using existing query logic (reusing strict logic)
        repo = SqlAlchemySubmissionReadRepository(db)
        query = GetStudentActivityDetails(repo)
        details = query.execute(activity_id, student_id)
        
        if not details:
            logger.error(f"Could not find details for analysis: {activity_id}, {student_id}")
            return

        logger.info(f"Analyzing Risk for {student_id}. Chat History Length: {len(details.chat_history)}")
        if details.chat_history:
            logger.info(f"First message: {details.chat_history[0]}")
            logger.info(f"Last message: {details.chat_history[-1]}")
        else:
            logger.warning("Chat history is EMPTY for this analysis!")

        # 2. Analyze
        analyzer = RiskAnalyzer()
        result = analyzer.analyze_student_risk(
            student_name=student_id,
            activity_title=details.activity_title,
            chat_history=details.chat_history,
            code_submission=details.code_submitted,
            grade=details.final_grade
        )
        
        # 3. Save Result
        # No serialization needed for JSON columns

        risk_model = RiskAnalysisModel(
            submission_id=submission_id,
            risk_score=result.get('risk_score', 0),
            risk_level=result.get('risk_level', 'LOW'),
            diagnosis=result.get('diagnosis', ''),
            evidence=result.get('evidence', []),
            teacher_advice=result.get('teacher_advice', ''),
            positive_aspects=result.get('positive_aspects', [])
        )
        
        # Upsert or Insert
        existing = db.query(RiskAnalysisModel).filter_by(submission_id=submission_id).first()
        if existing:
            db.delete(existing)
            
        db.add(risk_model)
        db.commit()
        logger.info(f"Risk analysis completed and saved for submission {submission_id}")

    except Exception as e:
        logger.error(f"Risk analysis failed for submission {submission_id}: {e}")
        db.rollback()
    finally:
        db.close()
