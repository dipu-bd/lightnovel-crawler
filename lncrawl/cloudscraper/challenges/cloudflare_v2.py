from __future__ import annotations

from copy import deepcopy
import json
import logging
import random
import re
import time
from typing import Callable
from urllib.parse import urljoin, urlparse

from requests import Response

from ..exceptions import (
    CloudflareCaptchaError,
    CloudflareChallengeError,
    CloudflareSolveError,
)
from .base import ChallengeHandler

logger = logging.getLogger(__name__)


class CloudflareV2Handler(ChallengeHandler):
    """Handles Cloudflare V2 JS orchestration challenges (jsch/v1 pattern)."""

    def __init__(self, *, debug: bool = False) -> None:
        self.debug = debug
        self._delay = random.uniform(1.0, 5.0)

    # -- Detection ----------------------------------------------------------

    def is_challenge(self, response: Response) -> bool:
        try:
            return (
                response.headers.get("Server", "").startswith("cloudflare")
                and response.status_code in (403, 429, 503)
                and bool(
                    re.search(
                        r"cpo\.src\s*=\s*['\"]\/cdn-cgi\/challenge-platform\/\S+orchestrate\/jsch\/v1",
                        response.text,
                        re.M | re.S,
                    )
                )
            )
        except AttributeError:
            return False

    @staticmethod
    def is_captcha_challenge(response: Response) -> bool:
        try:
            return (
                response.headers.get("Server", "").startswith("cloudflare")
                and response.status_code == 403
                and bool(
                    re.search(
                        r"cpo\.src\s*=\s*['\"]\/cdn-cgi\/challenge-platform\/\S+orchestrate\/(captcha|managed)\/v1",
                        response.text,
                        re.M | re.S,
                    )
                )
            )
        except AttributeError:
            return False

    # -- Solving ------------------------------------------------------------

    def handle(
        self,
        response: Response,
        *,
        request: Callable[..., Response],
        perform_request: Callable[..., Response],
        **kwargs,
    ) -> Response:
        if self.debug:
            logger.debug("CloudflareV2Handler: solving V2 challenge for %s", response.url)

        try:
            challenge_info = self._extract_challenge_data(response)
        except CloudflareChallengeError:
            raise

        time.sleep(self._delay)

        payload = self._build_payload(challenge_info["challenge_data"], response)
        url_parsed = urlparse(response.url)
        challenge_url = f"{url_parsed.scheme}://{url_parsed.netloc}{challenge_info['form_action']}"

        cf_kwargs = deepcopy(kwargs)
        cf_kwargs["allow_redirects"] = False
        cf_kwargs.setdefault("headers", {}).update(
            {
                "Origin": f"{url_parsed.scheme}://{url_parsed.netloc}",
                "Referer": response.url,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        challenge_resp = request("POST", challenge_url, data=payload, **cf_kwargs)

        if challenge_resp.status_code == 403:
            raise CloudflareSolveError("Cloudflare V2: challenge submission rejected (403).")

        if challenge_resp.is_redirect:
            redirect_url = challenge_resp.headers.get("Location", "")
            if not urlparse(redirect_url).netloc:
                redirect_url = urljoin(challenge_resp.url, redirect_url)
            follow_kwargs = deepcopy(kwargs)
            follow_kwargs.setdefault("headers", {}).update({"Referer": challenge_resp.url})
            return request(response.request.method, redirect_url, **follow_kwargs)

        return challenge_resp

    @staticmethod
    def _extract_challenge_data(resp: Response) -> dict:
        match = re.search(r"window\._cf_chl_opt=(\{.*?\});", resp.text, re.DOTALL)
        if not match:
            raise CloudflareChallengeError("CloudflareV2: could not find _cf_chl_opt data.")

        try:
            challenge_data = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise CloudflareChallengeError(
                f"CloudflareV2: malformed _cf_chl_opt JSON: {exc}"
            ) from exc

        form_match = re.search(
            r'<form .*?id="challenge-form" action="([^"]+)"',
            resp.text,
            re.DOTALL,
        )
        if not form_match:
            raise CloudflareChallengeError("CloudflareV2: could not find challenge form.")

        return {"challenge_data": challenge_data, "form_action": form_match.group(1)}

    @staticmethod
    def _build_payload(challenge_data: dict, resp: Response) -> dict:
        r_token = re.search(r'name="r" value="([^"]+)"', resp.text)
        if not r_token:
            raise CloudflareCaptchaError("CloudflareV2: could not find 'r' token.")

        payload: dict = {
            "r": r_token.group(1),
            "cf_ch_verify": "plat",
            "vc": "",
            "captcha_vc": "",
            "cf_captcha_kind": "h",
            "h-captcha-response": "",
        }

        if "cvId" in challenge_data:
            payload["cv_chal_id"] = challenge_data["cvId"]
        if "chlPageData" in challenge_data:
            payload["cf_chl_page_data"] = challenge_data["chlPageData"]

        return payload
