from __future__ import annotations

from typing import Any


class DecodoError(Exception):
    status_code: int
    api_status: str | None

    def __init__(self, message: str, status_code: int, api_status: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.api_status = api_status


class AuthenticationError(DecodoError):
    def __init__(self, message: str = "Authentication failed. Check your credentials.") -> None:
        super().__init__(message, 401, "failed")


class RateLimitError(DecodoError):
    def __init__(self, message: str = "Rate limit exceeded. Slow down your request rate.") -> None:
        super().__init__(message, 429, "failed")


class ValidationError(DecodoError):
    errors: list[Any] | None

    def __init__(self, message: str, errors: list[Any] | None = None) -> None:
        super().__init__(message, 422, "failed")
        self.errors = errors


class TimeoutError(Exception):
    def __init__(self, message: str = "The request timed out.") -> None:
        super().__init__(message)


class CrawlError(DecodoError):
    """Raised by ``crawl()`` when the crawl ends ``faulted`` or ``cancelled``."""

    crawl_id: str
    status: str
    reason: str | None

    def __init__(self, crawl_id: str, status: str, reason: str | None = None) -> None:
        detail = f" ({reason})" if reason else ""
        super().__init__(f"Crawl {crawl_id} ended with status {status}{detail}.", 200, status)
        self.crawl_id = crawl_id
        self.status = status
        self.reason = reason


class CrawlTimeoutError(TimeoutError):
    """Raised by ``crawl()`` when ``timeout`` elapses. The crawl keeps running on the server."""

    crawl_id: str

    def __init__(self, crawl_id: str, timeout: float) -> None:
        super().__init__(
            f"Crawl {crawl_id} did not finish within {timeout:g}s. "
            "It is still running: poll get_crawl_status, fetch get_crawl_results later, "
            "or stop it with cancel_crawl."
        )
        self.crawl_id = crawl_id
