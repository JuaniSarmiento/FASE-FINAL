import sys
import os
from sqlalchemy import inspect, text
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db

def inspect_schema():
    print("--- Inspecting DB Schema ---")
    db = next(get_db())
    inspector = inspect(db.get_bind())

    # 1. sessions_v2 columns
    if inspector.has_table("sessions_v2"):
        print("\nTable 'sessions_v2' columns:")
        for col in inspector.get_columns("sessions_v2"):
            print(f" - {col['name']} ({col['type']})")
    else:
        print("\n❌ Table 'sessions_v2' NOT FOUND.")

    # 2. tutor_messages columns
    if inspector.has_table("tutor_messages"):
        print("\nTable 'tutor_messages' columns:")
        for col in inspector.get_columns("tutor_messages"):
            print(f" - {col['name']} ({col['type']})")
        
        # Check FKs
        fks = inspector.get_foreign_keys("tutor_messages")
        print("\nFKs on 'tutor_messages':")
        for fk in fks:
            print(f" - {fk}")
    else:
        print("\n❌ Table 'tutor_messages' NOT FOUND.")

if __name__ == "__main__":
    inspect_schema()
