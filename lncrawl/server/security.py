from typing import Optional

from fastapi import Depends, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    SecurityScopes,
)

from ..context import ctx
from ..dao.user import User, UserRole
from ..exceptions import ServerErrors
from .models import LoginRequest

basic_auth = HTTPBasic(auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def ensure_user(
    security_scopes: SecurityScopes,
    basic: Optional[HTTPBasicCredentials] = Depends(basic_auth),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_auth),
) -> User:
    if basic:
        login = LoginRequest(
            email=basic.username,
            password=basic.password,
        )
        user = ctx.users.verify(login)
    elif bearer:
        required_scopes = security_scopes.scopes
        user = ctx.users.verify_token(bearer.credentials, required_scopes)
    else:
        raise ServerErrors.unauthorized
    if not user.is_active:
        raise ServerErrors.inactive_user
    return user


def ensure_admin(
    user: User = Security(ensure_user, scopes=[UserRole.ADMIN]),
) -> User:
    if user.role != UserRole.ADMIN:
        raise ServerErrors.forbidden
    return user


def ensure_local(
    user: User = Security(ensure_user, scopes=[UserRole.LOCAL]),
) -> User:
    if user.role != UserRole.ADMIN:
        raise ServerErrors.forbidden
    return user
