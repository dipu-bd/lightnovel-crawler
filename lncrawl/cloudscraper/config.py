from __future__ import annotations

from dataclasses import dataclass, field
import ssl
from typing import Callable

from requests import Response


@dataclass
class StealthConfig:
    enabled: bool = True
    # Delays when Cloudflare is active
    min_delay: float = 1.0
    max_delay: float = 3.0
    # Delays when no CF challenge has been seen (fast path)
    min_delay_fast: float = 0.0
    max_delay_fast: float = 0.1
    human_like_delays: bool = True
    randomize_headers: bool = True
    browser_quirks: bool = True


@dataclass
class ProxyConfig:
    proxy_urls: list[str] = field(default_factory=list)
    fallback_to_direct: bool = True
    tor_control_host: str = "127.0.0.1"
    tor_control_port: int = 9151
    tor_control_password: str = ""


@dataclass
class CloudScraperConfig:
    # Challenge handling
    disable_v1: bool = False
    disable_v2: bool = False
    disable_v3: bool = False
    disable_turnstile: bool = False
    solve_depth: int = 3
    double_down: bool = True

    # TLS
    cipher_suite: str | None = None
    ecdh_curve: str = "prime256v1"
    source_address: str | tuple | None = None
    server_hostname: str | None = None
    ssl_context: ssl.SSLContext | None = None
    rotate_tls_ciphers: bool = True

    # Session management
    session_refresh_interval: int = 3600
    auto_refresh_on_403: bool = True
    max_403_retries: int = 3

    # Request throttling
    min_request_interval: float = 2.0  # when CF protection is active
    min_request_interval_fast: float = 0.1  # when no CF has been detected
    max_concurrent_requests: int = 1

    # Stealth
    stealth: StealthConfig = field(default_factory=StealthConfig)

    # Browser / User-Agent
    browser: dict | None = None
    allow_brotli: bool = True

    # Proxy
    proxy: ProxyConfig = field(default_factory=ProxyConfig)

    # Hooks — invoked as pre_hook(scraper, method, url, *args, **kwargs) and
    # post_hook(scraper, response); both receive the CloudScraper instance.
    pre_hook: Callable[..., tuple] | None = None
    post_hook: Callable[..., Response] | None = None

    # SSL — set False to accept self-signed / expired certs manually;
    # the scraper also auto-retries with verify=False on SSLError for non-CF URLs.
    verify_ssl: bool = True

    # Debug
    debug: bool = False
