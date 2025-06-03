from fastapi import Depends
from fastapi.security import APIKeyHeader
from jose import jwt

from .context import ServerContext
from .exceptions import AppErrors
from .models.user import User, UserRole

header_scheme = APIKeyHeader(
    name='Authorization',
    scheme_name='Bearer Token',
)


def ensure_login(
    ctx: ServerContext = Depends(),
    token: str = Depends(header_scheme),
) -> dict:
    try:
        key = ctx.config.server.token_secret
        algo = ctx.config.server.token_algo
        if token.startswith('Bearer '):
            token = token[len('Bearer '):]
        return jwt.decode(token, key, algorithms=[algo])
    except Exception as e:
        raise AppErrors.unauthorized from e


def ensure_user(
    ctx: ServerContext = Depends(),
    payload: dict = Depends(ensure_login),
) -> User:
    user_id = payload.get('uid')
    if not user_id:
        raise AppErrors.unauthorized
    user = ctx.users.get(user_id)
    if not user.is_active:
        raise AppErrors.inactive_user
    return user


def ensure_admin(user: User = Depends(ensure_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise AppErrors.forbidden
    return user
