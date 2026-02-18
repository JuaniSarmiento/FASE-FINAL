import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/teacher"

try:
    # 1. Dashboard
    resp = requests.get(f"{BASE_URL}/dashboard")
    if resp.status_code == 200:
        print("Dashboard: OK", resp.json())
    else:
        print(f"Dashboard Failed: {resp.status_code} {resp.text}")

    # 2. Students
    resp = requests.get(f"{BASE_URL}/students")
    if resp.status_code == 200:
        print("Students List: OK", len(resp.json()))
    else:
        print(f"Students List Failed: {resp.status_code} {resp.text}")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
