from fastapi import APIRouter, Body, Depends, Path, Query, Security

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.pagination import Paginated
from ..models.user import CreateRequest, UpdateRequest, User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get('s', summary='Get list of all users')
def all_users(
    ctx: ServerContext = Depends(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[User]:
    return ctx.users.list(offset, limit)


@router.post('', summary='Create an user')
def create_user(
    ctx: ServerContext = Depends(),
    body: CreateRequest = Body(
        default=...,
        description='The signup request',
    ),
) -> User:
    return ctx.users.create(body)


@router.get('/{user_id}', summary='Get the user')
def get_user(
    ctx: ServerContext = Depends(),
    user_id: str = Path(),
) -> User:
    return ctx.users.get(user_id)


@router.put('/{user_id}', summary='Update the user')
def update_user(
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
    body: UpdateRequest = Body(
        default=...,
        description='The signup request',
    ),
    user_id: str = Path(),
) -> bool:
    if user_id == user.id:
        body.role = None
        body.is_active = None
    return ctx.users.update(user_id, body)


@router.delete('/{user_id}', summary='Delete the user')
def delete_user(
    user: User = Security(ensure_user),
    ctx: ServerContext = Depends(),
    user_id: str = Path(),
) -> bool:
    if user.id == user_id:
        raise AppErrors.can_not_delete_self
    return ctx.users.remove(user_id)
