from typing import Optional

from fastapi import Depends, Security
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBasic,
                              HTTPBasicCredentials, HTTPBearer, SecurityScopes)
from jose import jwt

from .context import ServerContext
from .exceptions import AppErrors
from .models.user import LoginRequest, User, UserRole

basic_auth = HTTPBasic(auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def ensure_user(
    security_scopes: SecurityScopes,
    ctx: ServerContext = Depends(),
    basic: Optional[HTTPBasicCredentials] = Depends(basic_auth),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_auth),
) -> User:
    try:
        if basic:
            login = LoginRequest(
                email=basic.username,
                password=basic.password,
            )
            user = ctx.users.verify(login)
        elif bearer:
            payload = jwt.decode(
                bearer.credentials,
                key=ctx.config.server.token_secret,
                algorithms=ctx.config.server.token_algo,
            )

            user_id = payload.get('uid')
            if not user_id:
                raise AppErrors.unauthorized

            token_scopes = payload.get('scopes', [])
            required_scopes = security_scopes.scopes
            if any(scope not in token_scopes for scope in required_scopes):
                raise AppErrors.forbidden

            user = ctx.users.get(user_id)
        else:
            raise AppErrors.unauthorized

        if not user.is_active:
            raise AppErrors.inactive_user
        return user
    except Exception as e:
        raise AppErrors.unauthorized from e


def ensure_admin(
    user: User = Security(ensure_user, scopes=[UserRole.ADMIN]),
) -> User:
    if user.role != UserRole.ADMIN:
        raise AppErrors.forbidden
    return user
