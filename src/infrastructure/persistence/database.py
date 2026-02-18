from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..config.settings import settings

# Force synchronous driver if asyncpg is provided by env
sync_url = settings.DATABASE_URL
if "+asyncpg" in sync_url:
    sync_url = sync_url.replace("+asyncpg", "")

engine = create_engine(
    sync_url, 
    pool_pre_ping=True, 
    echo=settings.DB_ECHO
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
