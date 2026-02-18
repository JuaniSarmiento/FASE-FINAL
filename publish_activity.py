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

def publish_activity():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Update 'Bucles 1' to published
            logger.info("Publishing activity 'Bucles 1' in Module 3...")
            connection.execute(text("UPDATE activities SET status = 'published' WHERE title = 'Bucles 1' AND type != 'module'"))
            connection.commit()
            logger.info("Activity published successfully!")
            
        except Exception as e:
            logger.error(f"Error publishing activity: {e}")

if __name__ == "__main__":
    publish_activity()
