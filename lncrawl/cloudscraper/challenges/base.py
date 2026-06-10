from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from requests import Response


class ChallengeHandler(ABC):
    """Stateless Cloudflare challenge handler.

    Handlers store only static config in __init__ — no back-reference to CloudScraper.
    Everything needed to solve a challenge is passed at call time via handle().
    """

    @abstractmethod
    def is_challenge(self, response: Response) -> bool:
        """Return True if this handler recognises the given response as its challenge type."""
        raise NotImplementedError()

    @abstractmethod
    def handle(
        self,
        response: Response,
        *,
        request: Callable[..., Response],
        perform_request: Callable[..., Response],
        **kwargs,
    ) -> Response:
        """Solve the challenge and return the final (non-challenge) response.

        Args:
            response: The challenge response from the server.
            request: The full CloudScraper.request callable — use this for POSTing challenge
                answers and fetching the final redirect destination so secondary challenges
                are handled automatically.
            perform_request: The raw Session.request callable — use this only for the
                doubleDown bypass attempt (bypasses the challenge loop).
            interpreter: The JavaScript interpreter for JS-based challenge solving.
            **kwargs: The original request kwargs (headers, data, etc.).
        """
        raise NotImplementedError()
