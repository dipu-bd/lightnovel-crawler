from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import json
import logging
import random
import re
import time
from typing import Callable
from urllib.parse import urljoin, urlparse

from requests import Response

from ..exceptions import CloudflareChallengeError, CloudflareSolveError
from .base import ChallengeHandler
from .interpreter import JavaScriptInterpreter

logger = logging.getLogger(__name__)


class CloudflareV3Handler(ChallengeHandler):
    """Handles Cloudflare V3 JavaScript VM challenges (jsch/v3 / _cf_chl_ctx pattern)."""

    def __init__(self, *, debug: bool = False) -> None:
        self.debug = debug
        self._delay = random.uniform(1.0, 5.0)

    # -- Detection ----------------------------------------------------------

    def is_challenge(self, response: Response) -> bool:
        try:
            return (
                response.headers.get("Server", "").startswith("cloudflare")
                and response.status_code in (403, 429, 503)
                and (
                    bool(
                        re.search(
                            r"cpo\.src\s*=\s*['\"]\/cdn-cgi\/challenge-platform\/\S+orchestrate\/jsch\/v3",
                            response.text,
                            re.M | re.S,
                        )
                    )
                    or bool(re.search(r"window\._cf_chl_ctx\s*=", response.text, re.M | re.S))
                    or bool(
                        re.search(
                            r'<form[^>]*id="challenge-form"[^>]*action="[^"]*__cf_chl_rt_tk=',
                            response.text,
                            re.M | re.S,
                        )
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
            logger.debug("CloudflareV3Handler: solving V3 VM challenge for %s", response.url)

        challenge_info = self._extract_data(response)
        time.sleep(self._delay)

        url_parsed = urlparse(response.url)
        interpreter = JavaScriptInterpreter()
        challenge_answer = self._execute_vm(challenge_info, url_parsed.netloc, interpreter)
        payload = self._build_payload(challenge_info, response, challenge_answer)

        challenge_url = challenge_info["form_action"]
        if not challenge_url.startswith("http"):
            challenge_url = f"{url_parsed.scheme}://{url_parsed.netloc}{challenge_url}"

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
            raise CloudflareSolveError("Cloudflare V3: challenge submission rejected (403).")

        if challenge_resp.is_redirect:
            redirect_url = challenge_resp.headers.get("Location", "")
            if not urlparse(redirect_url).netloc:
                redirect_url = urljoin(challenge_resp.url, redirect_url)
            follow_kwargs = deepcopy(kwargs)
            follow_kwargs.setdefault("headers", {}).update({"Referer": challenge_resp.url})
            return request(response.request.method, redirect_url, **follow_kwargs)

        return challenge_resp

    @staticmethod
    def _extract_data(resp: Response) -> dict:
        def _json(pattern: str) -> dict:
            m = re.search(pattern, resp.text, re.DOTALL)
            if not m:
                return {}
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                return {}

        ctx = _json(r"window\._cf_chl_ctx\s*=\s*(\{.*?\});")
        opt = _json(r"window\._cf_chl_opt\s*=\s*(\{.*?\});")

        form_m = re.search(
            r'<form[^>]*id="challenge-form"[^>]*action="([^"]+)"', resp.text, re.DOTALL
        )
        if not form_m:
            raise CloudflareChallengeError("CloudflareV3: could not find challenge form.")

        vm_m = re.search(
            r"<script[^>]*>\s*(.*?window\._cf_chl_enter.*?)</script>",
            resp.text,
            re.DOTALL,
        )

        return {
            "ctx_data": ctx,
            "opt_data": opt,
            "form_action": form_m.group(1),
            "vm_script": vm_m.group(1) if vm_m else None,
        }

    @staticmethod
    def _execute_vm(challenge_data: dict, domain: str, interpreter: JavaScriptInterpreter) -> str:
        vm_script = challenge_data.get("vm_script")
        if not vm_script:
            return CloudflareV3Handler._fallback_answer(challenge_data)

        js = f"""
        var window = {{
            location: {{href:"https://{domain}/",hostname:"{domain}",protocol:"https:",pathname:"/"}},
            navigator: {{userAgent:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                         platform:"Win32",language:"en-US"}},
            document: {{
                getElementById:function(id){{return{{value:"",style:{{}}}}}},
                createElement:function(tag){{return{{firstChild:{{href:"https://{domain}/"}},style:{{}}}}}}
            }},
            _cf_chl_ctx:{json.dumps(challenge_data.get("ctx_data", {}))},
            _cf_chl_opt:{json.dumps(challenge_data.get("opt_data", {}))},
            _cf_chl_enter:function(){{return true;}}
        }};
        var document=window.document;
        var location=window.location;
        var navigator=window.navigator;
        {vm_script}
        (typeof window._cf_chl_answer!=="undefined")?window._cf_chl_answer:
        (typeof _cf_chl_answer!=="undefined")?_cf_chl_answer:
        Math.random().toString(36).substring(2,15);
        """

        try:
            return str(interpreter.eval(js))
        except Exception as exc:
            logger.warning("CloudflareV3: VM execution failed (%s), using fallback.", exc)
            return CloudflareV3Handler._fallback_answer(challenge_data)

    @staticmethod
    def _fallback_answer(challenge_data: dict) -> str:
        opt = challenge_data.get("opt_data", {})
        ctx = challenge_data.get("ctx_data", {})
        if "chlPageData" in opt:
            return str(hash(opt["chlPageData"]) % 1_000_000)
        if "cvId" in ctx:
            return str(hash(ctx["cvId"]) % 1_000_000)
        return str(random.randint(100_000, 999_999))

    @staticmethod
    def _build_payload(challenge_data: dict, resp: Response, answer: str) -> OrderedDict:
        r_token = re.search(r'name="r" value="([^"]+)"', resp.text)
        if not r_token:
            raise CloudflareChallengeError("CloudflareV3: could not find 'r' token.")

        payload: OrderedDict = OrderedDict()
        payload["r"] = r_token.group(1)
        payload["jschl_answer"] = answer

        for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', resp.text):
            name, value = m.groups()
            if name not in payload:
                payload[name] = value

        return payload
