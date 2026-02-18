from fastapi import FastAPI
from src.infrastructure.http.routers.learning import generator_router
from src.infrastructure.http.routers.learning import rag_router
from src.infrastructure.http.routers.identity import auth_router
from src.infrastructure.http.routers.student import student_router
from src.infrastructure.http.routers.teacher import teacher_router
from src.infrastructure.http.routers.academic import academic_router
from src.infrastructure.http.routers.governance import governance_router
from src.infrastructure.http.routers.analytics import analytics_router
import src.infrastructure.persistence.models  # Register models
from src.infrastructure.persistence.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Fase Final MVP")



app.include_router(academic_router.router, prefix="/api/v1/academic", tags=["Academic"])
app.include_router(generator_router.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(rag_router.router, prefix="/api/v1/learning", tags=["RAG"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(student_router.router, prefix="/api/v1/student", tags=["Student"])
app.include_router(teacher_router.router, prefix="/api/v1/teacher", tags=["Teacher"])
app.include_router(governance_router.router, prefix="/api/v1/governance", tags=["Governance"])
app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health_check():
    return {"status": "ok"}
