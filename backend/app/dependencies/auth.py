from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.core.security import decode_access_token
from app.dependencies.db import DbSession
from app.exceptions import UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing authentication token")

    user_id = decode_access_token(credentials.credentials, settings)
    if user_id is None:
        raise UnauthorizedError("Invalid or expired token")

    user = await UserRepository(session).get_by_id(int(user_id))
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
