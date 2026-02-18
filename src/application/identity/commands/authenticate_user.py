from src.application.shared.unit_of_work import UnitOfWork
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.identity.ports.password_hasher import PasswordHasher
from src.domain.identity.ports.token_provider import ITokenProvider
from src.domain.identity.value_objects.email import Email
from src.application.identity.dtos.auth_dtos import LoginRequest, AuthResponseDTO, UserDTO, TokenDTO

class AuthenticateUser:
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

    def execute(self, request: LoginRequest) -> AuthResponseDTO:
        try:
            email_vo = Email(request.email)
        except ValueError as e:
             raise ValueError(f"Invalid email: {e}")

        user = self.user_repository.find_by_email(email_vo)
        if not user:
            raise ValueError("Invalid credentials")

        if not self.password_hasher.verify(request.password, user.hashed_password.value):
            raise ValueError("Invalid credentials")

        if not user.is_active:
             raise ValueError("User is inactive")

        # Generate Tokens
        token_data = {"sub": str(user.id.value), "role": user.roles[0].value}
        access_token = self.token_provider.create_access_token(token_data)
        refresh_token = self.token_provider.create_refresh_token(token_data)

        # Return DTO
        return AuthResponseDTO(
            user=UserDTO(
                id=str(user.id.value),
                email=user.email.address,
                role=user.roles[0].value,
                full_name=None, # Missing in User entity
                is_active=user.is_active
            ),
            tokens=TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
