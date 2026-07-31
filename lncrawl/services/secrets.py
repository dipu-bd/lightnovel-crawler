import logging
from typing import Any, List, Optional

from cryptography.fernet import Fernet
from scraper import extract_host
from sqlmodel import and_, col, func, select

from ..context import ctx
from ..dao import Secret
from ..exceptions import ServerErrors
from ..server.models import LoginData, Paginated

SECRET_KEY_ID = "--server-secret-key--"
logger = logging.getLogger(__name__)


class SecretService:
    def __init__(self) -> None:
        self._secret_key: Optional[bytes] = None

    def setup_secret(self) -> None:
        admin = ctx.users.get_admin()
        with ctx.db.session() as sess:
            secret = sess.get(Secret, SECRET_KEY_ID)
            if not secret:
                logger.info("Creating secret key")
                value = Fernet.generate_key()
                secret = Secret(
                    name=SECRET_KEY_ID,
                    user_id=admin.id,
                    value=value,
                )
                sess.add(secret)
                sess.commit()
        self._secret_key = secret.value

    def get_secret_key(self) -> bytes:
        if not self._secret_key:
            self.setup_secret()
            assert self._secret_key
        return self._secret_key

    def encrypt(self, value: bytes) -> bytes:
        key = self.get_secret_key()
        return Fernet(key).encrypt(value)

    def decrypt(self, value: bytes) -> bytes:
        key = self.get_secret_key()
        return Fernet(key).decrypt(value)

    def list(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
        search: str = "",
    ) -> Paginated[Secret]:
        with ctx.db.session() as sess:
            stmt = select(Secret)
            cnt = select(func.count()).select_from(Secret)

            # Apply filter
            conditions: List[Any] = []
            conditions.append(Secret.user_id == user_id)
            conditions.append(Secret.name != SECRET_KEY_ID)
            if search:
                conditions.append(col(Secret.name).ilike(f"%{search}%"))

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(col(Secret.created_at).desc())

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def add(
        self,
        user_id: str,
        name: str,
        value: str,
    ) -> Secret:
        if name == SECRET_KEY_ID:
            raise ServerErrors.invalid_input
        with ctx.db.session() as sess:
            secret = Secret(
                name=name,
                user_id=user_id,
                value=self.encrypt(value.encode()),
            )
            sess.add(secret)
            sess.commit()
            return secret

    def get(self, user_id: str, name: str) -> Secret:
        if name == SECRET_KEY_ID:
            raise ServerErrors.no_such_secret
        with ctx.db.session() as sess:
            secret = sess.get(Secret, name)
            if not secret or secret.user_id != user_id:
                raise ServerErrors.no_such_secret
            return secret

    def delete(self, user_id: str, name: str) -> None:
        if name == SECRET_KEY_ID:
            return
        with ctx.db.session() as sess:
            secret = sess.get(Secret, name)
            if not secret or secret.user_id != user_id:
                return
            sess.delete(secret)
            sess.commit()

    def get_value(self, user_id: str, name: str) -> Optional[str]:
        try:
            secret = self.get(user_id, name)
            return self.decrypt(secret.value).decode()
        except Exception:
            return None

    def add_login(self, user_id: str, url: str, login: LoginData) -> None:
        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        self.add(user_id, host, login.model_dump_json())

    def get_login(self, user_id: str, url: str) -> Optional[LoginData]:
        host = extract_host(url)
        value = self.get_value(user_id, host)
        if not value:
            return None
        return LoginData.model_validate_json(value)
