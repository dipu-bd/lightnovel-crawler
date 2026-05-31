import asyncio
import json
import logging
import time

from fastapi import APIRouter, Query, WebSocket, status

from ...context import ctx
from ...exceptions import WebSocketError
from ...services.lsp import _PROJECT_ROOT

logger = logging.getLogger(__name__)

router = APIRouter()

_VIRTUAL_ROOT = b"file:///workspace"
_PROJECT_URI = _PROJECT_ROOT.as_uri().encode()
_PYLSP_SETTINGS = {
    "signature": {
        "formatter": "ruff",
    },
    "plugins": {
        "jedi_completion": {
            "enabled": True,
            "include_params": True,
        },
        "jedi_definition": {
            "enabled": True,
            "follow_builtin_imports": True,
            "follow_imports": True,
        },
        "ruff": {
            # https://github.com/python-lsp/python-lsp-ruff
            "enabled": True,
            "preview": False,
            "unsafeFixes": False,
            "formatEnabled": True,
            "format": ["I", "E", "W", "F"],
            "select": ["I", "E", "W", "F"],
            "ignore": ["E203", "E265", "E501"],
            "lineLength": 100,
            "targetVersion": "py39",
        },
        "pyflakes": {
            "enabled": False,
        },
        "pycodestyle": {
            "enabled": False,
        },
        "autopep8": {
            "enabled": False,
        },
        "yapf": {
            "enabled": False,
        },
        "black": {
            "enabled": False,
        },
        "mccabe": {
            "enabled": False,
        },
        "pylsp_mypy": {
            "enabled": False,
        },
    },
}


async def _wait_for_lsp_ready(host: str, port: int, timeout: float = 5.0) -> bool:
    """Return True once the LSP port accepts TCP connections, False on timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            _, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return True
        except (ConnectionRefusedError, OSError):
            await asyncio.sleep(0.1)
    return False


def _translate_to_real(body: bytes) -> bytes:
    """Replace virtual workspace URIs with real filesystem paths for pylsp."""
    if _VIRTUAL_ROOT not in body:
        return body
    return body.replace(_VIRTUAL_ROOT, _PROJECT_URI)


def _translate_to_virtual(body: bytes) -> bytes:
    """Replace real filesystem URIs with virtual workspace URIs for the client."""
    if _PROJECT_URI not in body:
        return body
    return body.replace(_PROJECT_URI, _VIRTUAL_ROOT)


async def _relay_tcp(client: WebSocket, host: str, port: int) -> None:
    """Relay messages between the WebSocket client and pylsp over TCP."""
    reader, writer = await asyncio.open_connection(host, port)
    idle_timeout: float = ctx.config.lsp.idle_timeout
    last_activity = time.monotonic()
    config_sent = False

    async def _send_to_lsp(obj: dict) -> None:
        body = json.dumps(obj).encode()
        writer.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        await writer.drain()

    async def _send_config(body: bytes) -> None:
        # Inject _PYLSP_SETTINGS right after the client sends 'initialized'.
        nonlocal config_sent
        try:
            if json.loads(body).get("method") == "initialized":
                config_sent = True
                await _send_to_lsp(
                    {
                        "jsonrpc": "2.0",
                        "method": "workspace/didChangeConfiguration",
                        "params": {"settings": {"pylsp": _PYLSP_SETTINGS}},
                    }
                )
        except (json.JSONDecodeError, AttributeError):
            pass

    async def _forward_to_upstream():
        nonlocal last_activity
        try:
            while True:
                body = _translate_to_real((await client.receive_text()).encode())
                last_activity = time.monotonic()
                writer.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
                await writer.drain()
                if not config_sent:
                    await _send_config(body)
        except Exception:
            pass

    async def _forward_to_client():
        nonlocal last_activity
        try:
            while True:
                headers: dict[str, str] = {}
                while True:
                    line = (await reader.readline()).decode("ascii").strip()
                    if not line:
                        break
                    k, _, v = line.partition(":")
                    headers[k.strip().lower()] = v.strip()
                length = int(headers.get("content-length", 0))
                if not length:
                    break
                body = _translate_to_virtual(await reader.readexactly(length))
                last_activity = time.monotonic()
                await client.send_text(body.decode())
        except Exception:
            pass

    async def _idle_watcher():
        interval = min(30.0, idle_timeout / 6)
        while True:
            await asyncio.sleep(interval)
            if time.monotonic() - last_activity >= idle_timeout:
                logger.info("LSP session idle for %.0fs; closing", idle_timeout)
                return

    tasks = [
        asyncio.create_task(_forward_to_upstream()),
        asyncio.create_task(_forward_to_client()),
        asyncio.create_task(_idle_watcher()),
    ]
    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    writer.close()


@router.websocket("/lsp")
async def lsp_proxy(ws: WebSocket, token: str = Query()):
    """Proxy WebSocket connections to a dedicated pylsp subprocess."""
    try:
        user = ctx.users.verify_token(token)
        if not user.is_active and not user.is_admin:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        session = ctx.lsp.create_session()
    except WebSocketError as e:
        logger.info(f"LSP session rejected for user {user.id}", exc_info=True)
        await ws.close(code=e.code)
        return

    try:
        if not await _wait_for_lsp_ready(session.host, session.port):
            await ws.close(code=status.WS_1011_INTERNAL_ERROR)
            return

        await ws.accept()
        try:
            await _relay_tcp(ws, session.host, session.port)
        except Exception:
            logger.debug("LSP proxy session ended", exc_info=True)
    finally:
        session.stop()
