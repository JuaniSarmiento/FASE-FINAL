# Database Schema Documentation

This project uses PostgreSQL. The schema is automatically initialized from `init_schema.sql` for new instances.

## Inspection Tools

We provide a utility script to inspect the database tables and their contents.

### Windows
Double-click `inspect_db.bat` or run:
```cmd
.\inspect_db.bat
```

### Manual
You can also run the python script directly if you have the dependencies installed:
```bash
python scripts/inspect_db.py
```

## Tables Overview

- **users**: Stores user accounts, authentication info, and roles.
- **students** / **teachers**: Managed through roles in `users` table or separate specific tables if applicable (currently `users.roles`).
- **courses**: Academic courses.
- **subjects**: Subjects linked to courses.
- **activities**: Learning activities assigned to students.
- **sessions**: Tracking of student engagement with activities.
- **cognitive_traces**: AI-generated analysis of student performance.
- **incidents**: Reported issues or behavioral flags.

For a detailed view of columns, use the inspection tool.
