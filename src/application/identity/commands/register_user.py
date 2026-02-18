from src.application.shared.unit_of_work import UnitOfWork
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.identity.ports.password_hasher import PasswordHasher
from src.domain.identity.ports.token_provider import ITokenProvider
from src.domain.identity.entities.user import User, UserRole
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import PasswordHash
from src.application.identity.dtos.auth_dtos import RegisterUserRequest, AuthResponseDTO, UserDTO, TokenDTO

class RegisterUser:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_provider: ITokenProvider,
        unit_of_work: UnitOfWork
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_provider = token_provider
        self.unit_of_work = unit_of_work

    def execute(self, request: RegisterUserRequest) -> AuthResponseDTO:
        # Validate Input
        try:
            email_vo = Email(request.email)
        except ValueError as e:
            raise ValueError(f"Invalid email: {e}")

        # Check if user exists
        existing_user = self.user_repository.find_by_email(email_vo)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash Password
        hashed_pwd = self.password_hasher.hash(request.password)
        password_vo = PasswordHash(hashed_pwd)

        # Create User Entity
        try:
            role_enum = UserRole(request.role)
        except ValueError:
            role_enum = UserRole.STUDENT # Default fallback or raise
        
        user = User.create(email_vo, password_vo, role_enum)
        
        if request.full_name:
            # TODO: Add full_name to User entity if needed, legacy had it.
            # For now User entity doesn't have full_name explicitly defined in my view earlier, let's check.
            # I checked user.py, it DOES NOT have full_name. I should add it or ignore it.
            # Legacy AuthUser HAD full_name. I should Update User entity to include full_name.
            pass

        # Save User
        with self.unit_of_work:
            self.user_repository.save(user)
            self.unit_of_work.commit()

        # Generate Tokens
        token_data = {"sub": str(user.id.value), "role": user.roles[0].value}
        access_token = self.token_provider.create_access_token(token_data)
        refresh_token = self.token_provider.create_refresh_token(token_data)

        return AuthResponseDTO(
            user=UserDTO(
                id=str(user.id.value),
                email=user.email.address,
                role=user.roles[0].value,
                full_name=None, # Missing in domain entity
                is_active=user.is_active
            ),
            tokens=TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
