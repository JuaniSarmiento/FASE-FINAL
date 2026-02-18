import requests
import sys

try:
    # Check Health
    resp = requests.get("http://localhost:8000/health")
    if resp.status_code != 200:
        print(f"Health check failed: {resp.status_code}")
        sys.exit(1)
    print("Health check passed")

    # Check Auth Register (expect 422 Unprocessable Entity due to missing body)
    resp = requests.post("http://localhost:8000/api/v1/auth/register", json={})
    if resp.status_code == 422:
        print("Auth register endpoint exists and validates input")
    elif resp.status_code == 404:
        print("Auth register endpoint NOT FOUND")
        sys.exit(1)
    else:
        print(f"Auth register endpoint returned unexpected status: {resp.status_code}")

    # Check Auth Token (expect 422)
    resp = requests.post("http://localhost:8000/api/v1/auth/token", data={})
    if resp.status_code == 422:
        print("Auth token endpoint exists and validates input")
    elif resp.status_code == 404:
        print("Auth token endpoint NOT FOUND")
        sys.exit(1)
    else:
        print(f"Auth token endpoint returned unexpected status: {resp.status_code}")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
