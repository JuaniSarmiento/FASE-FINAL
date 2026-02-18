import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

# Create a student user first or assume one exists from previous steps (verify_student)
# We need a student ID. Let's register a new one to be safe or use hardcoded if known.
# Registering new user for academic test
email = "academic_student@test.com"
password = "password123"
try:
    auth_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "role": "student",
        "full_name": "Academic Student"
    })
    if auth_resp.status_code in [200, 201]:
        student_id = auth_resp.json()["id"]
        print(f"Registered Student: {student_id}")
    elif auth_resp.status_code == 400 and "already registered" in auth_resp.text:
       # Login to get ID? Or just fail if we can't get ID easily without login.
       # Login
       login_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
       if login_resp.status_code == 200:
           # We need ID, but login returns token and user info usually.
           # My auth_router returns token, user_id, role.
           student_id = login_resp.json()["user"]["id"]
           print(f"Logged in Student: {student_id}")
       else:
           print(f"Login failed: {login_resp.status_code} {login_resp.text}")
           sys.exit(1)
    else:
        print(f"Registration failed: {auth_resp.text}")
        sys.exit(1)

    import random
    suffix = random.randint(1000, 9999)
    subject_resp = requests.post(f"{BASE_URL}/academic/subjects", json={
        "name": f"Mathematics {suffix}",
        "code": f"MATH{suffix}",
        "description": "Calculus I"
    })
    if subject_resp.status_code == 200:
        subject_id = subject_resp.json()["id"]
        print(f"Created/Found Subject: {subject_id}")
    elif subject_resp.status_code == 500 and "duplicate key" in subject_resp.text:
         # In a real scenario we should get 400 or 409, but 500 is what we get now.
         # Ideally we query it. For now, let's try to fetch it if we can or assume ID issues.
         # Actually, better to make the test idempotent by using unique code each run or handling the error.
         # Let's generate a random code suffix.
         pass
    else:
        print(f"Create Subject Failed: {subject_resp.status_code} {subject_resp.text}")
        # sys.exit(1) # Don't exit yet, maybe we can recover? No, we need subject_id.
        pass

    # 2. Create Course
    course_resp = requests.post(f"{BASE_URL}/academic/courses", json={
        "subject_id": subject_id,
        "year": 2026,
        "semester": 1
    })
    if course_resp.status_code == 200:
        course_id = course_resp.json()["id"]
        print(f"Created Course: {course_id}")
    else:
        print(f"Create Course Failed: {course_resp.status_code} {course_resp.text}")
        sys.exit(1)

    # 3. Enroll Student
    enroll_resp = requests.post(f"{BASE_URL}/academic/enrollments", json={
        "student_id": student_id,
        "course_id": course_id
    })
    if enroll_resp.status_code == 200:
        enrollment_id = enroll_resp.json()["id"]
        print(f"Enrolled Student: {enrollment_id}")
    else:
        print(f"Enrollment Failed: {enroll_resp.status_code} {enroll_resp.text}")
        sys.exit(1)

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
