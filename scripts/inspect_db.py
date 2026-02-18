import os
from sqlalchemy import create_engine, inspect, text


# Determine if running inside docker or locally
if os.path.exists('/.dockerenv'):
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/ai_native")
else:
    # Local fallback
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5440/ai_native")

def inspect_db():
    print(f"Connecting to: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n--- Database Tables ---")
        for i, table in enumerate(tables):
            print(f"{i+1}. {table}")
            
        while True:
            choice = input("\nEnter table name to inspect (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                break
            
            if choice in tables:
                print(f"\n--- Schema for {choice} ---")
                columns = inspector.get_columns(choice)
                headers = ["Name", "Type", "Nullable", "Default"]
                table_data = [[c['name'], c['type'], c['nullable'], c['default']] for c in columns]
                import tabulate
                print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
                
                print(f"\n--- First 5 rows of {choice} ---")
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT * FROM {choice} LIMIT 5"))
                    rows = result.fetchall()
                    if rows:
                        print(tabulate.tabulate(rows, headers=result.keys(), tablefmt="grid"))
                    else:
                        print("No data found.")
            else:
                print("Table not found.")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure the database container is running (docker compose up -d db)")

if __name__ == "__main__":
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate...")
        os.system("pip install tabulate")
        import tabulate
        
    inspect_db()
