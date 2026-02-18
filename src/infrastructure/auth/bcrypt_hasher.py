import bcrypt
from src.domain.identity.ports.password_hasher import PasswordHasher

class BcryptHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        # bcrypt.hashpw requires bytes
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
