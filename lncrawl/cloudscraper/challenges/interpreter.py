"""JavaScript interpreter for solving Cloudflare challenges.

Backed by the embedded QuickJS engine. Cloudflare's IUAM (V1) challenges ship
obfuscated JavaScript that must be evaluated to compute the answer token.
"""

from __future__ import annotations

import logging
import re

import quickjs  # type:ignore

from ..exceptions import CloudflareSolveError

logger = logging.getLogger(__name__)

_BUG_REPORT = "Cloudflare may have changed their technique, or there may be a bug in the script."


def _iuam_template(body: str, domain: str) -> str:
    """Extract the Cloudflare IUAM challenge JS from *body* and wrap it in a
    browser-like environment so it can be evaluated by a plain JS engine."""

    match = re.search(
        r"setTimeout\(function\(\){\s+(.*?a\.value\s*=\s*\S+toFixed\(10\);)",
        body,
        re.M | re.S,
    )
    if match is None:
        raise ValueError(f"Unable to identify Cloudflare IUAM Javascript on website. {_BUG_REPORT}")
    js = match.group(1)

    js_env = (
        'String.prototype.italics=function(str) {{return "<i>" + this + "</i>"}};'
        "var subVars= {{{subVars}}};"
        "var document = {{"
        "createElement: function () {{"
        'return {{ firstChild: {{ href: "https://{domain}/" }} }}'
        "}},"
        "getElementById: function (str) {{"
        'return {{"innerHTML": subVars[str]}};'
        "}}"
        "}};"
    )

    try:
        js = js.replace(
            r"(setInterval(function(){}, 100),t.match(/https?:\/\//)[0]);",
            r"t.match(/https?:\/\//)[0];",
        )

        k_match = re.search(r" k\s*=\s*'(?P<k>\S+)';", body)
        if k_match is None:
            raise ValueError(f"Cloudflare IUAM 'k' variable not found. {_BUG_REPORT}")
        k = k_match.group("k")
        r = re.compile(r'<div id="{}(?P<id>\d+)">\s*(?P<jsfuck>[^<>]*)</div>'.format(k))

        sub_vars = ""
        for m in r.finditer(body):
            sub_vars = "{}\n\t\t{}{}: {},\n".format(sub_vars, k, m.group("id"), m.group("jsfuck"))
        sub_vars = sub_vars[:-2]

    except Exception:
        logger.error("Error extracting Cloudflare IUAM Javascript. %s", _BUG_REPORT)
        raise

    env_str = re.sub(
        r"\s{2,}",
        " ",
        js_env.format(domain=domain, subVars=sub_vars),
        flags=re.MULTILINE | re.DOTALL,
    )
    return f"{env_str}{js}"


class JavaScriptInterpreter:
    """Evaluates JavaScript using the embedded QuickJS engine."""

    def __init__(self) -> None:
        self._ctx = quickjs.Context()

    def eval(self, js: str) -> str:
        """Evaluate a JavaScript expression and return the result as a string."""
        return str(self._ctx.eval(js))

    def solve_challenge(self, body: str, domain: str) -> str:
        """Extract the CF IUAM challenge JS from *body* and evaluate it.

        Returns the numeric answer formatted to 10 decimal places, as CF expects.
        """
        try:
            result = self.eval(_iuam_template(body, domain))
            return "{:.10f}".format(float(result))
        except Exception as exc:
            raise CloudflareSolveError(
                "Error solving Cloudflare IUAM Javascript — CF may have changed their technique."
            ) from exc
