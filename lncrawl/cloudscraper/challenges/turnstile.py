from __future__ import annotations

import re
from typing import Callable

from requests import Response

from ..exceptions import CloudflareTurnstileError
from .base import ChallengeHandler


class TurnstileHandler(ChallengeHandler):
    """Detects Cloudflare Turnstile challenges.

    Turnstile requires a third-party captcha provider to solve.
    This handler raises :exc:`CloudflareTurnstileError` immediately because no
    provider is configured in lncrawl.
    """

    def is_challenge(self, response: Response) -> bool:
        try:
            if not response.headers.get("Server", "").startswith("cloudflare"):
                return False
            if response.status_code not in (403, 429, 503):
                return False
            text = response.text
            return (
                # Traditional explicit Turnstile embed
                bool(re.search(r'class="cf-turnstile"', text, re.M | re.S))
                or bool(
                    re.search(
                        r'src="https://challenges\.cloudflare\.com/turnstile/v0/api\.js',
                        text,
                        re.M | re.S,
                    )
                )
                or bool(re.search(r'data-sitekey="[0-9A-Za-z_-]{10,}"', text, re.M | re.S))
                # Modern managed challenge — Turnstile loaded dynamically by CF JS orchestrator
                or bool(re.search(r"window\._cf_chl_opt\s*=", text, re.M | re.S))
            )
        except AttributeError:
            return False

    def handle(
        self,
        response: Response,
        *,
        request: Callable[..., Response],
        perform_request: Callable[..., Response],
        **kwargs,
    ) -> Response:
        raise CloudflareTurnstileError(
            "Cloudflare Turnstile challenge detected. "
            "Solving Turnstile requires a captcha provider, which is not configured."
        )
