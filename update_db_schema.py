from src.infrastructure.persistence.database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as connection:
        # Add teacher_id column
        try:
            connection.execute(text("ALTER TABLE activities ADD COLUMN IF NOT EXISTS teacher_id VARCHAR DEFAULT 'default_teacher'"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_activities_teacher_id ON activities (teacher_id)"))
            connection.commit()
            print("Successfully added teacher_id column to activities table.")
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
