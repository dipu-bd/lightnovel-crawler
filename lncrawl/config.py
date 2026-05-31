from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from functools import cached_property
import json
import logging
import os
from pathlib import Path
import time
from typing import Annotated, Any, Callable, Dict, Optional, Type, TypeVar, Union, cast
import uuid

import dotenv
import typer

T = TypeVar("T")

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.absolute()
APP_DIR = Path(
    os.getenv("LNCRAWL_DATA_PATH")
    or typer.get_app_dir(
        "LNCrawl",
        force_posix=True,
        roaming=True,
    )
).absolute()
DEFAULT_CONFIG_FILE = APP_DIR / "config.json"


class Sensitive:
    """Use with `typing.Annotated` on config property return types.

    Properties marked this way are listed in the admin API with `sensitive=True`.
    """


# ------------------------------------------------------------------ #
#                            Utilitites                              #
# ------------------------------------------------------------------ #
def _serialize(obj: object) -> Any:
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)  # fallback for unknown types


def _deserialize(val: Any, typ: Type[T]) -> T:
    if val is None:
        return cast(T, None)
    if typ in (str, int, float, bool):
        return typ(val)  # type: ignore
    if typ == Decimal:
        return cast(T, Decimal(val))
    if typ == datetime:
        return cast(T, datetime.fromisoformat(val))
    if typ in (list, tuple, set):
        seq = json.loads(val) if isinstance(val, str) else val
        return cast(T, typ(seq))  # type: ignore
    if typ is dict:
        return cast(T, json.loads(val) if isinstance(val, str) else val)
    return cast(T, val)


def _traverse(obj: object) -> None:
    for name in dir(obj):
        if name.startswith("_"):
            continue
        attr = getattr(type(obj), name, None)
        if isinstance(attr, property) and attr.fset:
            value = getattr(obj, name)
            setattr(obj, name, value)
        elif isinstance(attr, cached_property):
            value = getattr(obj, name)
            if isinstance(value, _Section):
                _traverse(value)


def _merge(target: dict, source: dict) -> None:
    """Merge source into target, overriding existing values."""
    for key, value in source.items():
        if isinstance(target.get(key), dict) and isinstance(value, dict):
            _merge(target[key], value)
        else:
            target[key] = value


def _update(target: dict, source: dict) -> dict:
    """Update target with source, returning deprecated values."""
    deprecated = {}
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                inner = _update(target[key], value)
                if inner:
                    deprecated[key] = inner
            elif type(value) is type(target[key]):
                target[key] = value
            else:
                deprecated[key] = value
        else:
            deprecated[key] = value
    return deprecated


# ------------------------------------------------------------------ #
#                             Root Config                            #
# ------------------------------------------------------------------ #
class Config(object):
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.config_file: Optional[Path] = None
        self._data: Dict[str, Any] = {}
        _traverse(self)
        self._defaults = self._data.copy()

    @cached_property
    def app(self):
        """Application Settings."""
        return AppConfig(self)

    @cached_property
    def db(self):
        """Database Settings."""
        return DatabaseConfig(self)

    @cached_property
    def crawler(self):
        """Crawler Settings."""
        return CrawlerConfig(self)

    @cached_property
    def server(self):
        """Server Settings."""
        return ServerConfig(self)

    @cached_property
    def mail(self):
        """Mail Settings."""
        return MailConfig(self)

    @cached_property
    def lsp(self):
        """LSP Server Settings."""
        return PythonLanguageServerConfig(self)

    @cached_property
    def translator(self):
        """Translator Settings."""
        return TranslatorConfig(self)

    # -------------------------------------------------------------- #

    def load(self, file: Optional[Path] = None) -> None:
        """
        Loads configurations from given file, env var or default config.

        - Loads from param `file` if provided
        - Loads from `LNCRAWL_CONFIG` env var if available
        - Loads from default config file otherwise
        """
        env_file = os.getenv("LNCRAWL_CONFIG")
        if not file and env_file:
            file = Path(env_file)

        file = file or DEFAULT_CONFIG_FILE
        if file == self.config_file:
            return

        if file.is_file():
            try:
                source = json.loads(file.read_text(encoding="utf-8"))
                assert isinstance(source, dict)

                self.config_file = None
                self._data = self._defaults.copy()
                old_deprecated = source.pop("__deprecated__", {})
                new_deprecated = _update(self._data, source)
                _merge(new_deprecated, old_deprecated)

                if new_deprecated:
                    self._data["__deprecated__"] = new_deprecated
            except Exception:
                logger.error(f"Failed to load config file: {file}", exc_info=True)
                return

        self.config_file = file
        logger.info(f"Config file: {file}")

        self.save()

    def save(self) -> None:
        if not self.config_file:
            return
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        tid = time.thread_time_ns() % 1000
        tmp = self.config_file.with_suffix(f".json.tmp{tid}")
        content = json.dumps(self._data, indent=2, ensure_ascii=False)
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, self.config_file)

    # -------------------------------------------------------------- #

    def get(self, section: str, key: str, default: Union[None, T, Callable[[], T]] = None) -> Any:
        sub: dict = self._data.setdefault(section, {})
        if key not in sub:
            if callable(default):
                sub[key] = default()
            elif default is not None:
                sub[key] = default
            else:
                raise ValueError(f"{section}.{key} is not set")
        return _deserialize(sub[key], type(sub[key]))

    def set(self, section: str, key: str, value: Any) -> None:
        sub: dict = self._data.setdefault(section, {})
        if sub.get(key) is not None:
            value = _deserialize(value, type(sub[key]))
        sub[key] = _serialize(value)
        self.save()


# ------------------------------------------------------------------ #
#                            Section Base                            #
# ------------------------------------------------------------------ #
class _Section(object):
    section: str

    def __init__(self, parent: Config) -> None:
        self.root = parent
        if not self.section:
            raise ValueError(f"section is not defined for {self}")

    def _get(self, key: str, default: Union[T, Callable[[], Any]]) -> T:
        return self.root.get(self.section, key, default)

    def _set(self, key: str, value: Any) -> None:
        self.root.set(self.section, key, value)


# ------------------------------------------------------------------ #
#                             App Section                            #
# ------------------------------------------------------------------ #
class AppConfig(_Section):
    section = "app"
    name = "Lightnovel Crawler"

    @cached_property
    def version(self) -> str:
        return (ROOT_DIR / "VERSION").read_text(encoding="utf8").strip()

    @cached_property
    def app_dir(self) -> Path:
        return APP_DIR

    @property
    def openai_key(self) -> Annotated[str, Sensitive]:
        """OpenAI API Key.

        Your key for OpenAI or compatible APIs. Leave empty if you do not use those features.
        """
        return self._get("openai_api_key", "")

    @openai_key.setter
    def openai_key(self, v: str) -> None:
        self._set("openai_api_key", v)

    @property
    def github_token(self) -> Annotated[str, Sensitive]:
        """Github Token.

        Github token for creating automatic pull requests for sources.
        You can get one from here: https://github.com/settings/personal-access-tokens
        """
        return self._get("github_token", "")

    @github_token.setter
    def github_token(self, v: str) -> None:
        self._set("github_token", v)

    @property
    def admin_email(self) -> str:
        """Admin Email.

        Sign-in email for the built-in administrator account (for example in the web interface).
        The default is `"admin"`.
        """
        return self._get("admin_email", "admin")

    @admin_email.setter
    def admin_email(self, v: str) -> None:
        self._set("admin_email", v)

    @property
    def admin_password(self) -> Annotated[str, Sensitive]:
        """Admin Password.

        Password for the built-in administrator. Defaults to `"admin"`; choose a strong password
        on any shared or public setup.
        """
        return self._get("admin_password", "admin")

    @admin_password.setter
    def admin_password(self, v: str) -> None:
        self._set("admin_password", v)


# ------------------------------------------------------------------ #
#                         Translator Section                         #
# ------------------------------------------------------------------ #
class TranslatorConfig(_Section):
    section = "translator"

    @property
    def microsoft_translator_key(self) -> Annotated[str, Sensitive]:
        """Microsoft Translator API Key.

        Azure Cognitive Services key for the Translator resource. Free tier allows
        2,000,000 characters per month. Get one from: https://portal.azure.com
        """
        return self._get("microsoft_translator_key", "")

    @microsoft_translator_key.setter
    def microsoft_translator_key(self, v: str) -> None:
        self._set("microsoft_translator_key", v)

    @property
    def microsoft_translator_region(self) -> str:
        """Microsoft Translator Region.

        Azure region of your Translator resource, e.g. `eastus`. Required when using a
        multi-service or regional key; leave empty for global keys.
        """
        return self._get("microsoft_translator_region", "")

    @microsoft_translator_region.setter
    def microsoft_translator_region(self, v: str) -> None:
        self._set("microsoft_translator_region", v)

    @property
    def baidu_app_id(self) -> Annotated[str, Sensitive]:
        """Baidu Translate App ID.

        App ID for the Baidu Fanyi (translation) API. Particularly strong for Chinese,
        Japanese, and Korean. Register at: https://fanyi-api.baidu.com
        """
        return self._get("baidu_app_id", "")

    @baidu_app_id.setter
    def baidu_app_id(self, v: str) -> None:
        self._set("baidu_app_id", v)

    @property
    def baidu_secret_key(self) -> Annotated[str, Sensitive]:
        """Baidu Translate Secret Key.

        Secret key that pairs with your Baidu Translate App ID.
        """
        return self._get("baidu_secret_key", "")

    @baidu_secret_key.setter
    def baidu_secret_key(self, v: str) -> None:
        self._set("baidu_secret_key", v)


# ------------------------------------------------------------------ #
#                          Database Section                          #
# ------------------------------------------------------------------ #
class DatabaseConfig(_Section):
    section = "database"

    def __url(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        sqlite_url = f"sqlite:///{(APP_DIR / 'sqlite.db').resolve().as_posix()}"
        return env_url or sqlite_url

    @property
    def url(self) -> Annotated[str, Sensitive]:
        """Database URL.

        Where the app stores its data. If you omit this, it looks for a standard database
        environment variable first, then uses a small file-based database in your app data folder.

        Examples:
        - `sqlite:////full/path/to/sqlite.db`
        - `postgresql+psycopg://pguser:pgpass@postgres:5432/lncrawl`
        - `mysql+pymysql://user:password@mysql:3306/lncrawl`
        """
        return self._get("url", self.__url)

    @url.setter
    def url(self, v: str) -> None:
        self._set("url", v)

    @property
    def pool_size(self) -> int:
        """Connection Pool Size.

        How many database connections the app keeps ready at once. Higher can help under load.
        Default is `10`.
        """
        return self._get("pool_size", 10)

    @pool_size.setter
    def pool_size(self, v: int) -> None:
        self._set("pool_size", v)

    @property
    def pool_timeout(self) -> int:
        """Pool Connection Timeout.

        How many seconds to wait for a free database connection before giving up.
        Default is `30`.
        """
        return self._get("pool_timeout", 30)

    @pool_timeout.setter
    def pool_timeout(self, v: int) -> None:
        self._set("pool_timeout", v)

    @property
    def pool_recycle(self) -> int:
        """Pool Recycle Interval.

        After this many seconds, an old connection is replaced with a fresh one so dropped or idle
        links do not cause errors. Default is one hour (`3600`).
        """
        return self._get("pool_recycle", 3600)

    @pool_recycle.setter
    def pool_recycle(self, v: int) -> None:
        self._set("pool_recycle", v)

    @property
    def connect_timeout(self) -> int:
        """Database Connect Timeout.

        How long to wait when first connecting to the database, in seconds. Default is `10`.
        """
        return self._get("connect_timeout", 10)

    @connect_timeout.setter
    def connect_timeout(self, v: int) -> None:
        self._set("connect_timeout", v)


# ------------------------------------------------------------------ #
#                           Crawler Section                          #
# ------------------------------------------------------------------ #
class CrawlerConfig(_Section):
    section = "crawler"

    @cached_property
    def local_sources(self) -> Path:
        for dir in [ROOT_DIR, ROOT_DIR.parent]:
            folder = dir / "sources"
            if folder.is_dir():
                return folder
        raise ValueError("No local sources")

    @cached_property
    def local_index_file(self) -> Path:
        return self.local_sources / "_index.json"

    @cached_property
    def user_sources(self) -> Path:
        return APP_DIR / "sources"

    @cached_property
    def user_index_file(self) -> Path:
        return self.user_sources / "_index.json"

    @property
    def can_use_browser(self) -> bool:
        """Browser Crawling.

        Allow crawlers to drive a real browser for sites that need JavaScript. Turn off if you want
        to avoid browser automation entirely. On by default.
        """
        return self._get("can_use_browser", True)

    @can_use_browser.setter
    def can_use_browser(self, v: bool) -> None:
        self._set("can_use_browser", v)

    @property
    def selenium_grid(self) -> str:
        """Selenium Grid URL.

        Address of your Selenium Grid or remote browser hub, if you run browsers on another machine.
        You can set this here or leave it blank and define it in the environment instead.
        """
        return self._get("selenium_grid", os.getenv("SELENIUM_GRID", ""))

    @selenium_grid.setter
    def selenium_grid(self, url: str) -> None:
        self._set("selenium_grid", url)

    @property
    def index_file_download_url(self) -> str:
        """Sources Index Download URL.

        Where the app downloads the official list of site sources from. This is built in and does
        not appear in your settings file.
        """
        return "https://raw.githubusercontent.com/lncrawl/lightnovel-crawler/dev/sources/_index.zip"

    @property
    def ignore_images(self) -> bool:
        """Ignore Images When Crawling.

        Skip pictures and other images while downloading chapters to save space and time. Off by
        default.
        """
        return self._get("ignore_images", False)

    @ignore_images.setter
    def ignore_images(self, v: bool) -> None:
        self._set("ignore_images", v)

    @property
    def runner_concurrency(self) -> int:
        """Runner Concurrency.

        How many crawl jobs may run at the same time. Default is `5`.
        """
        return self._get("runner_concurrency", 5)

    @runner_concurrency.setter
    def runner_concurrency(self, v: int) -> None:
        self._set("runner_concurrency", v)

    @property
    def runner_cooldown(self) -> int:
        """Runner Cooldown.

        Short pause in seconds between scheduler checks so the system is not constantly busy.
        Default is `1`.
        """
        return self._get("runner_cooldown", 1)

    @runner_cooldown.setter
    def runner_cooldown(self, v: int) -> None:
        self._set("runner_cooldown", v)

    @property
    def disk_size_limit(self) -> int:
        """Disk Size Limit.

        Cap on how much disk space downloaded novels may use, measured in bytes. Zero means no limit.
        Default is `0`.
        """
        mb = self._get("disk_size_limit_mb", 0)
        return mb * 1024 * 1024

    @disk_size_limit.setter
    def disk_size_limit(self, bytes_val: int) -> None:
        mb = None if bytes_val is None else bytes_val // (1024 * 1024)
        self._set("disk_size_limit_mb", mb)

    @property
    def scrubber_cooldown(self) -> int:
        """Scrubber Cooldown.

        Minimum time in seconds between background cleanup passes. Default is half an hour
        (`1800` seconds).
        """
        return self._get("cleaner_cooldown", 30 * 60)

    @scrubber_cooldown.setter
    def scrubber_cooldown(self, v: int) -> None:
        self._set("cleaner_cooldown", v)

    @property
    def runner_reset_interval(self) -> int:
        """Runner Reset Interval.

        How often the crawl scheduler fully restarts itself, in seconds, to stay healthy. Default
        is four hours (`14400`).
        """
        return self._get("runner_reset_interval", 4 * 3600)

    @runner_reset_interval.setter
    def runner_reset_interval(self, v: int) -> None:
        self._set("runner_reset_interval", v)


# ------------------------------------------------------------------ #
#                           Server Section                           #
# ------------------------------------------------------------------ #
class ServerConfig(_Section):
    section = "server"

    @property
    def base_url(self) -> str:
        """Server Base URL.

        The address users and other services should use to reach the app (no trailing slash).
        Important for correct links and sign-in redirects. Local default is
        `http://localhost:8181`.
        """
        return self._get("base_url", "http://localhost:8181").strip("/")

    @base_url.setter
    def base_url(self, v: str) -> None:
        self._set("base_url", v)

    @property
    def token_secret(self) -> Annotated[str, Sensitive]:
        """JWT Token Secret.

        Private value used to sign login sessions. If you do not set one, the app generates and
        remembers a random value for you; set it yourself if several servers must agree on the
        same secret.
        """
        return self._get("token_secret", lambda: str(uuid.uuid4()))

    @token_secret.setter
    def token_secret(self, v: str) -> None:
        self._set("token_secret", v)

    @property
    def token_algo(self) -> str:
        """JWT Signing Algorithm.

        Cryptographic method used to sign session tokens. The usual default `HS256` is fine for
        most deployments.
        """
        return self._get("token_algorithm", "HS256")

    @token_algo.setter
    def token_algo(self, v: str) -> None:
        self._set("token_algorithm", v)

    @property
    def token_expiry(self) -> int:
        """JWT Token Expiry.

        How long a sign-in stays valid, in minutes. Default is one week (`10080` minutes).
        """
        return self._get("token_expiry_minutes", lambda: 7 * 24 * 60)

    @token_expiry.setter
    def token_expiry(self, v: int) -> None:
        self._set("token_expiry_minutes", v)


# ------------------------------------------------------------------ #
#                            Mail Section                            #
# ------------------------------------------------------------------ #
class MailConfig(_Section):
    section = "mail"

    @property
    def smtp_server(self) -> str:
        """SMTP Server.

        Host name or IP of the machine that sends your email. `localhost` is common when testing
        with a local mail catcher.
        """
        return self._get("smtp_server", "localhost")

    @smtp_server.setter
    def smtp_server(self, v: str) -> None:
        self._set("smtp_server", v)

    @property
    def smtp_port(self) -> int:
        """SMTP Port.

        Network port for mail submission. `1025` matches many simple local test setups; production
        often uses `587` or `465`.
        """
        return self._get("smtp_port", 1025)

    @smtp_port.setter
    def smtp_port(self, v: int) -> None:
        self._set("smtp_port", v)

    @property
    def smtp_username(self) -> str:
        """SMTP Username.

        Login name for your mail provider, if it requires authentication. Leave empty when the
        server does not ask for a user.
        """
        return self._get("smtp_username", "")

    @smtp_username.setter
    def smtp_username(self, v: str) -> None:
        self._set("smtp_username", v)

    @property
    def smtp_password(self) -> Annotated[str, Sensitive]:
        """SMTP Password.

        Password that goes with the mail login, when your provider needs one. Leave empty if not
        required.
        """
        return self._get("smtp_password", "")

    @smtp_password.setter
    def smtp_password(self, v: str) -> None:
        self._set("smtp_password", v)

    @property
    def smtp_sender(self) -> str:
        """SMTP Sender Address.

        The From address recipients see, for example `no-reply@example.com`. Some providers
        require this to match an allowed sender.
        """
        return self._get("smtp_sender", "")

    @smtp_sender.setter
    def smtp_sender(self, v: str) -> None:
        self._set("smtp_sender", v)


# ------------------------------------------------------------------ #
#                   PythonLanguageServer Section                             #
# ------------------------------------------------------------------ #


class PythonLanguageServerConfig(_Section):
    section = "lsp"

    @property
    def enabled(self) -> bool:
        """LSP Server Enabled.

        Start a python-lsp-server process alongside the web server so editors
        can connect for code intelligence on crawler sources. Requires the
        `lsp` optional dependency to be installed. Off by default.
        """
        return self._get("enabled", False)

    @enabled.setter
    def enabled(self, v: bool) -> None:
        self._set("enabled", v)

    @property
    def host(self) -> str:
        """LSP Server Host.

        Address the language server binds to. Use `127.0.0.1` (default) to
        allow only local connections, or `0.0.0.0` to accept remote clients.
        Only applies to `tcp` mode; WebSocket mode always binds all interfaces.
        """
        return self._get("host", "127.0.0.1")

    @host.setter
    def host(self, v: str) -> None:
        self._set("host", v)

    @property
    def port(self) -> int:
        """LSP Server Port.

        Network port for the language server. Setting it to 0 will choose
        a random free port. Default is `0`.
        """
        return self._get("port", 0)

    @port.setter
    def port(self, v: int) -> None:
        self._set("port", v)

    @property
    def max_sessions(self) -> int:
        """LSP Max Simultaneous Sessions.

        Maximum number of pylsp processes that may run at the same time.
        Each WebSocket connection spawns one process, so this is effectively
        the concurrent-user cap for the language server. Default is `3`.
        """
        return self._get("max_sessions", 3)

    @max_sessions.setter
    def max_sessions(self, v: int) -> None:
        self._set("max_sessions", v)

    @property
    def idle_timeout(self) -> int:
        """LSP Idle Timeout (seconds).

        Seconds of inactivity after which an LSP session is automatically
        closed. Activity is defined as any message in either direction.
        Default is `1800` (30 minutes).
        """
        return self._get("idle_timeout", 1800)

    @idle_timeout.setter
    def idle_timeout(self, v: int) -> None:
        self._set("idle_timeout", v)
