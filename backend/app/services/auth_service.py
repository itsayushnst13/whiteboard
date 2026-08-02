from app.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies.db import DbSession
from app.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    """Registration and login. Issues stateless JWT access tokens rather
    than server-side sessions, so no session store is needed."""

    def __init__(self, session: DbSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def register(self, payload: RegisterRequest, settings: Settings) -> TokenResponse:
        existing = await self._users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists")

        user = await self._users.create(
            User(
                email=payload.email,
                hashed_password=hash_password(payload.password),
                display_name=payload.display_name,
            )
        )
        await self._session.commit()
        return self._issue_token(user, settings)

    async def login(self, payload: LoginRequest, settings: Settings) -> TokenResponse:
        user = await self._users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        return self._issue_token(user, settings)

    def _issue_token(self, user: User, settings: Settings) -> TokenResponse:
        token = create_access_token(str(user.id), settings)
        return TokenResponse(
            access_token=token,
            user=UserResponse(id=user.id, email=user.email, display_name=user.display_name),
        )
