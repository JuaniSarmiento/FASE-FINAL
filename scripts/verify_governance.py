import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

# Scenario:
# 1. Login as Student (Academic Student from previous step)
# 2. Report an Incident
# 3. List Incidents

email = "academic_student@test.com"
password = "password123"

try:
    # 1. Login
    print(f"Logging in as {email}...")
    login_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
    
    if login_resp.status_code == 200:
        token = login_resp.json()["tokens"]["access_token"]
        # Safe access to user_id
        student_id = login_resp.json()["user"]["id"]
        print(f"Logged in. Student ID: {student_id}")
    else:
        print(f"Login failed: {login_resp.status_code} {login_resp.text}")
        # If student doesn't exist (e.g. fresh db), we might need to register.
        # But we assume sequential execution or existing DB.
        sys.exit(1)

    # 2. Report Incident
    print("Reporting Incident...")
    incident_resp = requests.post(f"{BASE_URL}/governance/incidents", json={
        "student_id": student_id,
        "incident_type": "academic_integrity",
        "description": "I found a resource that might be plagiarized in the library.",
        "severity": "medium"
    })
    
    if incident_resp.status_code == 201:
        incident_id = incident_resp.json()["id"]
        print(f"Reported Incident: {incident_id}")
    else:
        print(f"Report Incident Failed: {incident_resp.status_code} {incident_resp.text}")
        sys.exit(1)

    # 3. List Incidents
    print("Listing Incidents...")
    list_resp = requests.get(f"{BASE_URL}/governance/incidents")
    
    if list_resp.status_code == 200:
        incidents = list_resp.json()
        print(f"Found {len(incidents)} incidents.")
        found = False
        for inc in incidents:
            if inc["id"] == incident_id:
                print(f"Verified Incident {incident_id} is in list.")
                found = True
                break
        if not found:
            print("New incident not found in list!")
            sys.exit(1)
    else:
        print(f"List Incidents Failed: {list_resp.status_code} {list_resp.text}")
        sys.exit(1)
        
    print("Governance Module Verified Successfully!")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
