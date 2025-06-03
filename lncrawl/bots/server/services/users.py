from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlmodel import func, select

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.pagination import Paginated
from ..models.user import (LoginRequest, CreateRequest, UpdateRequest, User,
                           UserRole)


class UserService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db
        self._passlib = CryptContext(
            schemes=['argon2'],
            deprecated='auto',
        )
        self.__prepare_admin()

    def _hash(self, plain_password: str) -> str:
        return self._passlib.hash(plain_password)

    def _check(self, plain: str, hashed: str) -> bool:
        return self._passlib.verify(plain, hashed)

    def __prepare_admin(self):
        with self._db.session() as sess:
            email = self._ctx.config.server.admin_email
            password = self._ctx.config.server.admin_password
            q = select(User).where(User.email == email)
            user = sess.exec(q).first()
            if not user:
                user = User(
                    email=email,
                    is_active=True,
                    name="Server Admin",
                    role=UserRole.ADMIN,
                    password=self._hash(password),
                )
            else:
                user.is_active = True
                user.role = UserRole.ADMIN
                user.password = self._hash(password)
            sess.add(user)
            sess.commit()

    def generate_token(self, user_id: str) -> str:
        key = self._ctx.config.server.token_secret
        algorithm = self._ctx.config.server.token_algo
        minutes = self._ctx.config.server.token_expiry
        expiry = datetime.now() + timedelta(minutes=minutes)
        payload = {
            'uid': user_id,
            'exp': expiry
        }
        return jwt.encode(payload, key, algorithm)

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
