from __future__ import annotations


class CloudflareException(Exception):
    """Base exception for all cloudscraper Cloudflare errors."""


class CloudflareLoopProtection(CloudflareException):
    """Raised when the challenge-solve recursion depth limit is exceeded."""


class CloudflareCode1020(CloudflareException):
    """Raised when Cloudflare returns a 1020 (firewall block) response."""


class CloudflareIUAMError(CloudflareException):
    """Raised when IUAM challenge parameters cannot be extracted or evaluated."""


class CloudflareChallengeError(CloudflareException):
    """Raised when an unsupported Cloudflare challenge version is detected."""


class CloudflareSolveError(CloudflareException):
    """Raised when the challenge answer is rejected by Cloudflare."""


class CloudflareCaptchaError(CloudflareException):
    """Raised when a captcha-only CF challenge is detected (no provider available)."""


class CloudflareTurnstileError(CloudflareException):
    """Raised when a Cloudflare Turnstile challenge is detected (requires a captcha provider)."""


class CloudflareV3Error(CloudflareException):
    """Raised when a Cloudflare V3 JavaScript VM challenge cannot be solved."""


class AbortedException(CloudflareException):
    """Raised when a request is aborted via the abort signal."""
