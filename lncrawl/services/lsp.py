import importlib.util
import logging
import os
from pathlib import Path
import subprocess
import sys
from threading import Event, Lock, Thread
from typing import IO, List, Optional

from ..context import ctx
from ..exceptions import WebSocketErros
from ..utils.platforms import Platform
from ..utils.sockets import free_port

# Canonical project root: one level above the `lncrawl` package directory.
# Used as pylsp's cwd so it discovers pyproject.toml and the sources/ tree.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

logger = logging.getLogger(__name__)


class PyLSP_Session:
    """A single dedicated pylsp process for one WebSocket client."""

    def __init__(self, host: str, port: int, env: dict) -> None:
        self._signal = Event()
        self._process: Optional[subprocess.Popen[str]] = None
        self.host = host
        self.port = port
        self._env = env

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> None:
        cmd = self._build_cmd()
        logger.info("Starting LSP session: %s", " ".join(cmd))
        extra: dict = (
            {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
            if sys.platform == "win32"
            else {"start_new_session": True}
        )
        self._process = subprocess.Popen(
            cmd,
            cwd=str(_PROJECT_ROOT),
            env=self._env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            **extra,
        )
        self._start_pipe_reader(self._process.stdout, logging.DEBUG)
        self._start_pipe_reader(self._process.stderr, logging.DEBUG)
        logger.info(
            "LSP session started (pid=%d) on %s:%d", self._process.pid, self.host, self.port
        )

    def stop(self) -> None:
        if not self._process or not self.is_running:
            return
        self._signal.set()
        pid = self._process.pid
        logger.info("Stopping LSP session (pid=%d)", pid)
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("LSP session (pid=%d) did not exit cleanly; killing", pid)
            self._process.kill()
            self._process.wait()
        self._process = None
        logger.info("LSP session stopped")

    def _build_cmd(self) -> List[str]:
        if Platform.frozen:
            exe = [sys.executable]
        else:
            exe = [sys.executable, "-m", "pylsp"]
        return exe + [
            "-vvv",
            "--tcp",
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

    def _start_pipe_reader(self, pipe: Optional[IO[str]], level: int) -> None:
        if pipe is None:
            return

        def _drain():
            for line in pipe:
                if self._signal.is_set():
                    break
                line = line.rstrip("\n")
                if line:
                    logger.log(level, "[pylsp] %s", line)

        Thread(target=_drain, daemon=True, name=f"lsp-reader-{level}").start()


class PythonLanguageServer:
    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: List[PyLSP_Session] = []
        self.host = ctx.config.lsp.host

    @staticmethod
    def is_available() -> bool:
        return importlib.util.find_spec("pylsp") is not None

    def create_session(self) -> PyLSP_Session:
        """Spawn a dedicated pylsp process for one client.

        Raises error if the session cap is reached or LSP is unavailable.
        Caller is responsible for calling session.stop() on exit.
        """
        if not ctx.config.lsp.enabled or not self.is_available():
            raise WebSocketErros.lsp_unavailable

        with self._lock:
            self._sessions = [s for s in self._sessions if s.is_running]
            if len(self._sessions) >= ctx.config.lsp.max_sessions:
                raise WebSocketErros.lsp_session_limit

            host = "127.0.0.1" if self.host == "0.0.0.0" else self.host
            port = free_port(host, 0)
            session = PyLSP_Session(host, port, self._build_env())
            session.start()
            self._sessions.append(session)

        return session

    def stop(self) -> None:
        with self._lock:
            sessions, self._sessions = self._sessions, []
        for s in sessions:
            try:
                s.stop()
            except Exception:
                pass

    def _build_env(self) -> dict:
        env = os.environ.copy()
        extra: List[str] = []

        if Platform.frozen:
            env["LNCRAWL_PYLSP"] = "1"
            meipass = getattr(sys, "_MEIPASS", "")
            if meipass:
                env["_MEIPASS2"] = meipass
        else:
            extra.append(str(_PROJECT_ROOT))

        for path in [ctx.config.crawler.user_sources]:
            if path.exists():
                extra.append(str(path))

        if extra:
            existing = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = os.pathsep.join([*extra, existing] if existing else extra)

        return env
