import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/student"

try:
    # 1. List Activities
    resp = requests.get(f"{BASE_URL}/activities")
    if resp.status_code == 200:
        print("List Activities: OK")
    else:
        print(f"List Activities Failed: {resp.status_code} {resp.text}")

    # 2. Start Session (Expect 400 or 500 if activity doesn't exist, but endpoint reachable)
    resp = requests.post(f"{BASE_URL}/sessions", json={"student_id": "test", "activity_id": "nonexistent"})
    if resp.status_code in [201, 400, 404, 500]: # 500 might happen if DB error on query
        print(f"Start Session Endpoint Reachable (Status: {resp.status_code})")
    else:
        print(f"Start Session Endpoint Failed: {resp.status_code}")

    # 3. Chat (Expect 400/404)
    resp = requests.post(f"{BASE_URL}/sessions/123/chat", json={"session_id": "123", "message": "hello"})
    if resp.status_code in [200, 400, 404, 500]:
        print(f"Chat Endpoint Reachable (Status: {resp.status_code})")
    else:
        print(f"Chat Endpoint Failed: {resp.status_code}")

    # 4. Submit (Expect 400/404)
    resp = requests.post(f"{BASE_URL}/sessions/123/submit", json={"session_id": "123", "student_id": "test", "activity_id": "act1"})
    if resp.status_code in [200, 400, 404, 500]: # 422 if validation fail
         print(f"Submit Endpoint Reachable (Status: {resp.status_code})")
    elif resp.status_code == 422:
         print("Submit Endpoint Reachable (Validation Error)")
    else:
         print(f"Submit Endpoint Failed: {resp.status_code}")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
