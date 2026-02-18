import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.infrastructure.auth.bcrypt_hasher import BcryptHasher

def test_hashing():
    hasher = BcryptHasher()
    password = "password123"
    print(f"Testing hashing with password: '{password}' (len={len(password)})")
    
    try:
        hashed = hasher.hash(password)
        print(f"Hashed result: {hashed}")
        print("Success!")
    except Exception as e:
        print(f"Error hashing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hashing()
