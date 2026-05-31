from typing import List

from fastapi import APIRouter, Body, Form, Query, Security

from ...context import ctx
from ...dao import ActivityType, User, UserToken
from ..models import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    NameUpdateRequest,
    PasswordUpdateRequest,
    ResetPasswordRequest,
    SendInviteRequest,
    SignupRequest,
    TokenResponse,
    UpdateRequest,
)
from ..security import ensure_user

# The root router
router = APIRouter()


@router.post("/login", summary="Login with username or email and password")
def login(
    credentials: LoginRequest = Body(
        default=...,
        description="The login credentials",
    ),
) -> LoginResponse:
    user = ctx.users.verify(credentials)
    token = ctx.users.generate_token(user)
    return LoginResponse(
        token=token,
        user=user,
    )


@router.post("/signup", summary="Signup as a new user")
def signup(
    body: SignupRequest = Body(
        default=...,
        description="The signup request",
    ),
) -> LoginResponse:
    user = ctx.users.signup(body)
    token = ctx.users.generate_token(user)
    return LoginResponse(
        token=token,
        user=user,
    )


@router.get("/me", summary="Get current user details")
def me(
    user: User = Security(ensure_user),
) -> User:
    ctx.activity.record(user.id, ActivityType.ACCOUNT, user.id)
    return user


@router.delete("/me", summary="Deactivate current user")
def delete_me(
    user: User = Security(ensure_user),
) -> bool:
    ctx.users.update(user.id, UpdateRequest(is_active=False))
    return True


@router.put("/me/name", summary="Update current user name")
def self_name_update(
    user: User = Security(ensure_user),
    body: NameUpdateRequest = Body(description="The update request"),
) -> bool:
    request = UpdateRequest(name=body.name)
    ctx.users.update(user.id, request)
    return True


@router.put("/me/password", summary="Update current user password")
def self_password_update(
    user: User = Security(ensure_user),
    body: PasswordUpdateRequest = Body(description="The update request"),
) -> bool:
    ctx.users.change_password(user, body)
    return True


@router.post("/send-password-reset-link", summary="Send reset password link to email")
def send_password_reset_link(
    body: ForgotPasswordRequest = Body(description="The request body"),
) -> bool:
    ctx.users.send_password_reset_link(body.email)
    return True


@router.post("/reset-password-with-token", summary="Verify token and change password")
def reset_password_with_token(
    user: User = Security(ensure_user),
    body: ResetPasswordRequest = Body(description="The request body"),
) -> bool:
    request = UpdateRequest(password=body.password)
    ctx.users.update(user.id, request)
    ctx.users.set_verified(user.email)
    return True


@router.post("/me/send-otp", summary="Send OTP to current user email for verification")
def send_otp(
    user: User = Security(ensure_user),
) -> TokenResponse:
    token = ctx.users.send_otp(user.email)
    return TokenResponse(token=token)


@router.post("/verify-otp", summary="Verify OTP and set user as verified")
def verify_otp(
    otp: str = Form(),
    token: str = Form(),
) -> bool:
    ctx.users.verify_otp(token, otp)
    return True


@router.post("/me/create-token", summary="Generate a user token")
def generate_my_token(
    user: User = Security(ensure_user),
) -> TokenResponse:
    token = ctx.users.get_signup_token(user)
    return TokenResponse(token=token)


@router.get("/verify-token", summary="Verify a user token")
def verify_user_token(token: str = Query(description="User token")) -> bool:
    user = ctx.users.verify_user_token(token)
    return user.is_active


@router.post("/me/tokens", summary="List all of my tokens")
def list_my_tokens(
    user: User = Security(ensure_user),
) -> List[UserToken]:
    return ctx.users.list_user_tokens(user.id)


@router.post("/me/send-invite", summary="Send a signup invitation email with referral token")
def send_invite(
    user: User = Security(ensure_user),
    body: SendInviteRequest = Body(description="The invite request"),
) -> bool:
    ctx.users.send_invite_email(user, body.email)
    return True
