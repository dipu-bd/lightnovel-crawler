from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import html
import logging
import re
import time
from typing import Callable
from urllib.parse import urljoin, urlparse

from requests import Response

from ..exceptions import (
    CloudflareCaptchaError,
    CloudflareChallengeError,
    CloudflareCode1020,
    CloudflareIUAMError,
    CloudflareSolveError,
)
from .base import ChallengeHandler
from .interpreter import JavaScriptInterpreter

logger = logging.getLogger(__name__)


class CloudflareV1Handler(ChallengeHandler):
    """Handles legacy Cloudflare IUAM (I'm Under Attack Mode) V1 JS challenges."""

    def __init__(self, *, debug: bool = False, double_down: bool = True) -> None:
        self.debug = debug
        self.double_down = double_down

    # -- Detection ----------------------------------------------------------

    def is_challenge(self, response: Response) -> bool:
        try:
            server = response.headers.get("Server", "")
            if not server.startswith("cloudflare"):
                return False

            if self._is_firewall_blocked(response):
                raise CloudflareCode1020("Cloudflare has blocked this request (Code 1020).")

            if self._is_new_captcha_challenge(response) or self._is_new_iuam_challenge(response):
                raise CloudflareChallengeError(
                    "Detected a Cloudflare V2 challenge — handled by CloudflareV2Handler."
                )

            if self._is_captcha_challenge(response):
                raise CloudflareCaptchaError(
                    "Cloudflare captcha challenge detected; no captcha provider is configured."
                )

            return self._is_iuam_challenge(response)
        except (CloudflareCode1020, CloudflareChallengeError, CloudflareCaptchaError):
            raise
        except AttributeError:
            return False

    @staticmethod
    def _is_iuam_challenge(resp: Response) -> bool:
        try:
            return (
                resp.headers.get("Server", "").startswith("cloudflare")
                and resp.status_code in (429, 503)
                and bool(re.search(r"/cdn-cgi/images/trace/jsch/", resp.text, re.M | re.S))
                and bool(
                    re.search(
                        r'<form .*?="challenge-form" action="/\S+__cf_chl_f_tk=',
                        resp.text,
                        re.M | re.S,
                    )
                )
            )
        except AttributeError:
            return False

    @staticmethod
    def _is_captcha_challenge(resp: Response) -> bool:
        try:
            return (
                resp.headers.get("Server", "").startswith("cloudflare")
                and resp.status_code == 403
                and bool(
                    re.search(r"/cdn-cgi/images/trace/(captcha|managed)/", resp.text, re.M | re.S)
                )
                and bool(
                    re.search(
                        r'<form .*?="challenge-form" action="/\S+__cf_chl_f_tk=',
                        resp.text,
                        re.M | re.S,
                    )
                )
            )
        except AttributeError:
            return False

    @staticmethod
    def _is_firewall_blocked(resp: Response) -> bool:
        try:
            return (
                resp.headers.get("Server", "").startswith("cloudflare")
                and resp.status_code == 403
                and bool(
                    re.search(
                        r'<span class="cf-error-code">1020</span>', resp.text, re.M | re.DOTALL
                    )
                )
            )
        except AttributeError:
            return False

    @staticmethod
    def _is_new_iuam_challenge(resp: Response) -> bool:
        try:
            return CloudflareV1Handler._is_iuam_challenge(resp) and bool(
                re.search(
                    r"cpo\.src\s*=\s*['\"]\/cdn-cgi\/challenge-platform\/\S+orchestrate\/jsch\/v1",
                    resp.text,
                    re.M | re.S,
                )
            )
        except AttributeError:
            return False

    @staticmethod
    def _is_new_captcha_challenge(resp: Response) -> bool:
        try:
            return CloudflareV1Handler._is_captcha_challenge(resp) and bool(
                re.search(
                    r"cpo\.src\s*=\s*['\"]\/cdn-cgi\/challenge-platform\/\S+orchestrate\/(captcha|managed)\/v1",
                    resp.text,
                    re.M | re.S,
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
            logger.debug("CloudflareV1Handler: solving IUAM challenge for %s", response.url)

        # doubleDown: retry the original request first; CF sometimes clears on second attempt
        if self.double_down:
            second = perform_request(response.request.method, response.url, **kwargs)
            if not self._is_iuam_challenge(second):
                return second

        interpreter = JavaScriptInterpreter()
        submit = self._build_iuam_payload(response.text, response.url, interpreter)
        return self._submit(submit, response, request, **kwargs)

    def _build_iuam_payload(self, body: str, url: str, interpreter: JavaScriptInterpreter) -> dict:
        form_match = re.search(
            r'<form (?P<form>.*?="challenge-form" '
            r'action="(?P<uuid>.*?__cf_chl_f_tk=\S+)"(.*?)</form>)',
            body,
            re.M | re.DOTALL,
        )
        if form_match is None:
            raise CloudflareIUAMError("Cloudflare IUAM: could not extract form parameters.")
        form = form_match.groupdict()

        if not all(k in form for k in ("form", "uuid")):
            raise CloudflareIUAMError("Cloudflare IUAM: form parameters incomplete.")

        payload: OrderedDict = OrderedDict()
        for param in re.findall(r"^\s*<input\s(.*?)/>", form["form"], re.M | re.S):
            kv = dict(re.findall(r'(\S+)="(\S+)"', param))
            if kv.get("name") in ("r", "jschl_vc", "pass"):
                payload[kv["name"]] = kv["value"]

        # Extract delay from JS
        delay = 4.0
        delay_match = re.search(r"submit\(\);\r?\n\s*},\s*([0-9]+)", body)
        if delay_match:
            try:
                delay = float(delay_match.group(1)) / 1000
            except ValueError:
                pass
        logger.debug("CloudflareV1: waiting %.1fs before challenge submit", delay)
        time.sleep(delay)

        try:
            payload["jschl_answer"] = interpreter.solve_challenge(body, urlparse(url).netloc)
        except Exception as exc:
            raise CloudflareIUAMError(
                f"CloudflareV1: JS challenge evaluation failed: {exc}"
            ) from exc

        parsed = urlparse(url)
        return {
            "url": f"{parsed.scheme}://{parsed.netloc}{html.unescape(form['uuid'])}",
            "data": payload,
        }

    @staticmethod
    def _submit(
        submit: dict,
        original_response: Response,
        request: Callable[..., Response],
        **kwargs,
    ) -> Response:
        cf_kwargs = deepcopy(kwargs)
        cf_kwargs["allow_redirects"] = False
        cf_kwargs.setdefault("data", {}).update(submit["data"])

        parsed = urlparse(original_response.url)
        cf_kwargs.setdefault("headers", {}).update(
            {
                "Origin": f"{parsed.scheme}://{parsed.netloc}",
                "Referer": original_response.url,
            }
        )

        challenge_resp = request("POST", submit["url"], **cf_kwargs)

        if challenge_resp.status_code == 400:
            raise CloudflareSolveError(
                "Invalid challenge answer — Cloudflare rejected the submission."
            )

        if not challenge_resp.is_redirect:
            return challenge_resp

        # Follow the redirect manually so the full request loop handles any further challenges
        redirect_url = challenge_resp.headers.get("Location", "")
        if not urlparse(redirect_url).netloc:
            redirect_url = urljoin(challenge_resp.url, redirect_url)

        follow_kwargs = deepcopy(kwargs)
        follow_kwargs.setdefault("headers", {}).update({"Referer": challenge_resp.url})
        return request(original_response.request.method, redirect_url, **follow_kwargs)
