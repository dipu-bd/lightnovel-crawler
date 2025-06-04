from fastapi import APIRouter, Body, Depends

from ..context import ServerContext
from ..models.user import (CreateRequest, LoginRequest, LoginResponse,
                           SignupRequest, UpdateRequest, User)
from ..security import ensure_user

# The root router
router = APIRouter()


@router.post("/login", summary="Login with username or email and password")
def login(
    ctx: ServerContext = Depends(),
    credentials: LoginRequest = Body(
        default=...,
        description='The login credentials',
    ),
):
    user = ctx.users.verify(credentials)
    token = ctx.users.generate_token(user.id)
    return LoginResponse(token=token, user=user)


@router.post('/signup', summary='Signup as a new user')
def signup(
    ctx: ServerContext = Depends(),
    body: SignupRequest = Body(
        default=...,
        description='The signup request',
    ),
):
    request = CreateRequest(
        password=body.password,
        email=body.email,
        name=body.name,
    )
    user = ctx.users.create(request)
    token = ctx.users.generate_token(user.id)
    return LoginResponse(token=token, user=user)


@router.get('/me', summary='Get current user details')
def me(
    user: User = Depends(ensure_user),
):
    return user


@router.put('/me/update', summary='Update current user details')
def self_update(
    ctx: ServerContext = Depends(),
    user: User = Depends(ensure_user),
    body: UpdateRequest = Body(
        default=...,
        description='The signup request',
    ),
):
    body.role = None
    body.tier = None
    body.is_active = None
    return ctx.users.update(user.id, body)
