import requests
import sys
import os
sys.path.append(os.getcwd())
from src.infrastructure.config.settings import settings

def check_ollama():
    # When running from host, use localhost. 
    # When running in docker, use settings.OLLAMA_BASE_URL (http://ollama:11434)
    # This script is for host execution.
    url = "http://localhost:11434" 
    print(f"--- Checking Ollama Connection (from Host) ---")
    print(f"URL: {url}")
    
    # 1. Check Version
    try:
        print(f"Attempting GET {url}/api/version ...")
        res = requests.get(f"{url.rstrip('/')}/api/version", timeout=5)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"❌ Version check failed: {e}")

    # 2. Check Generation (Quick)
    try:
        model = "llama3:1b"
        print(f"\nAttempting Generation with model='{model}'...")
        payload = {
            "model": model,
            "prompt": "Say hi",
            "stream": False
        }
        res = requests.post(f"{url.rstrip('/')}/api/generate", json=payload, timeout=10)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(f"Response: {res.json().get('response')}")
        else:
            print(f"Error Response: {res.text}")
            
    except Exception as e:
        print(f"❌ Generation check failed: {e}")

if __name__ == "__main__":
    check_ollama()
