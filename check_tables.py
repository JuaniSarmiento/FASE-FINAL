from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5440/ai_native")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Existing tables: {tables}")
if 'activity_assignments' in tables and 'activity_documents' in tables:
    print("SUCCESS: New tables found.")
else:
    print("WARNING: New tables NOT found.")
