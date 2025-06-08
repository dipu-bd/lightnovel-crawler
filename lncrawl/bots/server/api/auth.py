from fastapi import APIRouter, Body, Depends, Security, Form

from ..context import ServerContext
from ..models.user import (CreateRequest, LoginRequest, LoginResponse,
                           SignupRequest, TokenResponse, UpdateRequest, User)
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
) -> LoginResponse:
    user = ctx.users.verify(credentials)
    token = ctx.users.generate_token(user)
    is_verified = ctx.users.is_verified(user.email)
    return LoginResponse(
        token=token,
        user=user,
        is_verified=is_verified,
    )


@router.post('/signup', summary='Signup as a new user')
def signup(
    ctx: ServerContext = Depends(),
    body: SignupRequest = Body(
        default=...,
        description='The signup request',
    ),
) -> LoginResponse:
    request = CreateRequest(
        password=body.password,
        email=body.email,
        name=body.name,
    )
    user = ctx.users.create(request)
    token = ctx.users.generate_token(user)
    is_verified = ctx.users.is_verified(user.email)
    return LoginResponse(
        token=token,
        user=user,
        is_verified=is_verified,
    )


@router.get('/me', summary='Get current user details')
def me(
    user: User = Security(ensure_user),
) -> User:
    return user


@router.put('/me/update', summary='Update current user details')
def self_update(
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
    body: UpdateRequest = Body(
        default=...,
        description='The signup request',
    ),
) -> bool:
    body.role = None
    body.tier = None
    body.is_active = None
    return ctx.users.update(user.id, body)


@router.post('/me/send-otp', summary='Send OTP to current user email for verification')
def send_otp(
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
) -> TokenResponse:
    token = ctx.users.send_otp(user.email)
    return TokenResponse(token=token)


@router.post('/me/verify-otp', summary='Get if current user email is verified')
def verify_otp(
    otp: str = Form(),
    token: str = Form(),
    ctx: ServerContext = Depends(),
) -> bool:
    return ctx.users.verify_otp(token, otp)
