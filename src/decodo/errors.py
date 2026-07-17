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
