from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.auth_service import AuthService
from app.services.board_service import BoardService
from app.services.health_service import HealthService

SettingsDep = Annotated[Settings, Depends(get_settings)]
HealthServiceDep = Annotated[HealthService, Depends(HealthService)]
AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
BoardServiceDep = Annotated[BoardService, Depends(BoardService)]
