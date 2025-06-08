import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from jose import jwt
from passlib.context import CryptContext
from sqlmodel import func, select

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.pagination import Paginated
from ..models.user import (CreateRequest, LoginRequest, UpdateRequest, User,
                           UserRole, UserTier, VerifiedEmail)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db
        self._passlib = CryptContext(
            schemes=['argon2'],
            deprecated='auto',
        )

    def _hash(self, plain_password: str) -> str:
        return self._passlib.hash(plain_password)

    def _check(self, plain: str, hashed: str) -> bool:
        return self._passlib.verify(plain, hashed)

    def prepare(self):
        with self._db.session() as sess:
            email = self._ctx.config.server.admin_email
            password = self._ctx.config.server.admin_password
            q = select(User).where(User.email == email)
            user = sess.exec(q).first()
            if not user:
                logger.info('Adding admin user')
                user = User(
                    email=email,
                    password=self._hash(password),
                    name="Server Admin",
                    role=UserRole.ADMIN,
                    tier=UserTier.VIP,
                )
            else:
                logger.info('Updating admin user')
                user.is_active = True
                user.role = UserRole.ADMIN
                user.tier = UserTier.VIP
                user.password = self._hash(password)
            sess.add(user)
            sess.commit()

    def encode_token(
        self,
        payload: Dict[str, Any],
        expiry_minutes: Optional[int] = None,
    ) -> str:
        key = self._ctx.config.server.token_secret
        algorithm = self._ctx.config.server.token_algo
        default_expiry = self._ctx.config.server.token_expiry
        minutes = expiry_minutes if expiry_minutes else default_expiry
        payload['exp'] = datetime.now() + timedelta(minutes=minutes)
        return jwt.encode(payload, key, algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            key = self._ctx.config.server.token_secret
            algorithm = self._ctx.config.server.token_algo
            return jwt.decode(token, key, algorithm)
        except Exception as e:
            raise AppErrors.unauthorized from e

    def generate_token(self, user: User) -> str:
        payload = {
            'uid': user.id,
            'scopes': [user.role, user.tier],
        }
        return self.encode_token(payload)

    def verify_token(self, token: str, required_scopes: List[str]) -> User:
        payload = self.decode_token(token)
        user_id = payload.get('uid')
        token_scopes = payload.get('scopes', [])
        if not user_id:
            raise AppErrors.unauthorized
        if any(scope not in token_scopes for scope in required_scopes):
            raise AppErrors.forbidden
        return self.get(user_id)

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[User]:
        with self._db.session() as sess:
            q = select(User).offset(offset).limit(limit)
            users = sess.exec(q).all()
            total = sess.exec(select(func.count()).select_from(User)).one()
            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(users),
            )

    def get(self, user_id: str) -> User:
        with self._db.session() as sess:
            user = sess.get(User, user_id)
            if not user:
                raise AppErrors.no_such_user
            return user

    def verify(self, creds: LoginRequest) -> User:
        with self._db.session() as sess:
            q = select(User).where(User.email == creds.email)
            user = sess.exec(q).first()
            if not user:
                raise AppErrors.no_such_user
            if not user.is_active:
                raise AppErrors.inactive_user
        if not self._check(creds.password, user.password):
            raise AppErrors.unauthorized
        return user

    def create(self, body: CreateRequest) -> User:
        with self._db.session() as sess:
            q = select(func.count()).where(User.email == body.email)
            if sess.exec(q).one() != 0:
                raise AppErrors.user_exists
            user = User(
                name=body.name,
                email=body.email,
                role=body.role,
                tier=body.tier,
                password=self._hash(body.password),
            )
            sess.add(user)
            sess.commit()
            sess.refresh(user)
            return user

    def update(self, user_id: str, body: UpdateRequest) -> bool:
        with self._db.session() as sess:
            user = sess.get(User, user_id)
            if not user:
                raise AppErrors.no_such_user

            updated = False
            if body.name is not None:
                user.name = body.name
                updated = True
            if body.password is not None:
                user.password = self._hash(body.password)
                updated = True
            if body.role is not None:
                user.role = body.role
                updated = True
            if body.tier is not None:
                user.tier = body.tier
                updated = True
            if body.is_active is not None:
                user.is_active = body.is_active
                updated = True

            if updated:
                sess.add(user)
                sess.commit()
            return updated

    def remove(self, user_id: str) -> bool:
        with self._db.session() as sess:
            user = sess.get(User, user_id)
            if not user:
                raise AppErrors.no_such_user
            sess.delete(user)
            sess.commit()
            return True

    def is_verified(self, email: str) -> bool:
        with self._db.session() as sess:
            verified = sess.get(VerifiedEmail, email)
            return bool(verified)

    def send_otp(self, email: str):
        with self._db.session() as sess:
            verified = sess.get(VerifiedEmail, email)
            if verified:
                raise AppErrors.email_already_verified

        otp = str(secrets.randbelow(1000000)).zfill(6)
        self._ctx.mail.send_otp(email, otp)
        return self.encode_token({
            'otp': otp,
            'email': email,
        }, 5)

    def verify_otp(self, token: str, input_otp: str) -> bool:
        payload = self.decode_token(token)
        email = payload.get('email')
        if not email:
            raise AppErrors.not_found

        actual_otp = payload.get('otp')
        if actual_otp != input_otp:
            raise AppErrors.unauthorized

        with self._db.session() as sess:
            entry = VerifiedEmail(email=email)
            sess.add(entry)
            sess.commit()
            return True
