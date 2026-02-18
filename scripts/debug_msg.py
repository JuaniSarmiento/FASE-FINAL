import psycopg2
import sys

def test_connect():
    try:
        print("Attempting connection to 127.0.0.1:5433 as postgres/postgres...")
        conn = psycopg2.connect(
            dbname="ai_native",
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5433"
        )
        print("✅ SUCCESS!")
        conn.close()
    except Exception as e:
        print(f"❌ FAIL: {e}")

if __name__ == "__main__":
    test_connect()
