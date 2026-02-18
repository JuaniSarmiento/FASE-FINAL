import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from src.infrastructure.persistence.database import get_db

def debug_activities():
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("--- Debugging Activities Hierarchy ---\n")
        db = next(get_db())
        
        # Get all activities
        rows = db.execute(text("SELECT id, title, type, course_id, status, created_at FROM activities ORDER BY created_at DESC")).fetchall()
        
        modules = [r for r in rows if r.type == 'module']
        others = [r for r in rows if r.type != 'module']
        
        f.write(f"\nFOUND {len(modules)} MODULES and {len(others)} ACTIVITIES.\n")
        
        for m in modules:
            f.write(f"\n[MODULE] {m.title} ({m.status}) ID: {m.id} | Course: {m.course_id} | Created: {m.created_at}\n")
            children = [o for o in others if o.course_id == m.id]
            if children:
                for c in children:
                    f.write(f"   -> [{c.status}] {c.type}: {c.title} (ID: {c.id}) | Created: {c.created_at}\n")
            else:
                f.write("   -> (No children)\n")

        f.write("\n--- ORPHANS (course_id='default_course') ---\n")
        orphans = [o for o in others if o.course_id == 'default_course']
        for o in orphans:
            f.write(f" [ORPHAN] {o.title} ({o.status}) ID: {o.id} | Created: {o.created_at}\n")

if __name__ == "__main__":
    debug_activities()
