from typing import Optional
from sqlalchemy.orm import Session
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.identity.entities.user import User, UserRole
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.user_id import UserId
from src.domain.identity.value_objects.password import PasswordHash
from src.infrastructure.persistence.models.user_models import UserModel

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> None:
        user_model = self.db.query(UserModel).filter(UserModel.id == str(user.id.value)).first()
        if user_model:
            # Update
            user_model.email = user.email.address
            user_model.hashed_password = user.hashed_password.value
            user_model.roles = [r.value for r in user.roles]
            user_model.is_active = user.is_active
            user_model.is_verified = user.is_verified
            user_model.updated_at = user.updated_at
        else:
            # Create
            user_model = UserModel(
                id=str(user.id.value),
                email=user.email.address,
                hashed_password=user.hashed_password.value,
                roles=[r.value for r in user.roles],
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.db.add(user_model)
        # Flush is handled by UnitOfWork usually, but we can flush here if needed by ID generation
        # internal logic implies explicit commit/flush by UoW.
        
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == str(user_id.value)).first()
        if not model:
            return None
        return self._to_entity(model)

    def find_by_email(self, email: Email) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email.address).first()
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, user_id: UserId) -> None:
        self.db.query(UserModel).filter(UserModel.id == user_id.value).delete()

    def find_all_by_role(self, role_name: str) -> list[User]:
        # Using SQLAlchemy ANY or contains for ARRAY
        try:
            return [
                self._to_entity(m) 
                for m in self.db.query(UserModel).filter(UserModel.roles.contains([role_name])).all()
            ]
        except Exception:
            # Fallback if DB doesn't support array contains or similar
            # Fetch all and filter in python (inefficient but safe for MVP)
            all_users = self.db.query(UserModel).all()
            return [
                self._to_entity(m) 
                for m in all_users if role_name in m.roles
            ]

    def _to_entity(self, model: UserModel) -> User:
        user = User(
            id=UserId(model.id),
            email=Email(model.email),
            hashed_password=PasswordHash(model.hashed_password),
            roles=[UserRole(r) for r in model.roles],
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
        return user
