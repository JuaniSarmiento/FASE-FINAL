import sys
import os

# Adds the project root to sys.path
sys.path.append(r"c:\Users\juani\Desktop\FASE MVP\Fase Final")

import logging
from sqlalchemy import create_engine, text
from src.infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_activities():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            logger.info("--- Modules ---")
            modules = connection.execute(text("SELECT id, title, status FROM activities WHERE type = 'module' AND title LIKE '%Modulo 3%'")).fetchall()
            for m in modules:
                logger.info(f"Module: {m.title} (ID: {m.id}, Status: {m.status})")
                
                # Get activities for this module
                activities = connection.execute(text("SELECT id, title, status, type FROM activities WHERE course_id = :module_id"), {"module_id": m.id}).fetchall()
                if not activities:
                     logger.info(f"  No activities found for module {m.title}")
                for a in activities:
                    logger.info(f"  - Activity: {a.title} (ID: {a.id}, Type: {a.type}, Status: {a.status})")
                    
        except Exception as e:
            logger.error(f"Error listing activities: {e}")

if __name__ == "__main__":
    list_activities()
