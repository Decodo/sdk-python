from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from .errors import (
    AuthenticationError,
    DecodoError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)


@dataclass
class BasicAuth:
    type: str  # "basic"
    token: str


@dataclass
class ApiKeyAuth:
    type: str  # "apiKey"
    api_key: str


@dataclass
class HttpClientConfig:
    base_url: str
    auth: BasicAuth | ApiKeyAuth
    timeout_ms: int
    integration_header: str | None = None


class HttpClient:
    def __init__(self, config: HttpClientConfig) -> None:
        self._base_url = config.base_url.rstrip("/")
        self._timeout_ms = config.timeout_ms
        self._integration_header = config.integration_header or "sdk-python"

        if config.auth.type == "basic":
            assert isinstance(config.auth, BasicAuth)
            self._auth_header = f"Basic {config.auth.token}"
        else:
            assert isinstance(config.auth, ApiKeyAuth)
            self._auth_header = f"Bearer {config.auth.api_key}"

    def request(self, method: str, path: str, body: Any = None) -> Any:
        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": self._auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-integration": self._integration_header,
        }
        timeout = self._timeout_ms / 1000.0

        try:
            response = httpx.request(
                method,
                url,
                headers=headers,
                json=body,
                timeout=timeout,
            )
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Request to {path} timed out after {self._timeout_ms}ms"
            )

        if response.is_success:
            if response.status_code == 204:
                return None
            return response.json()

        error_body: dict[str, Any] | None = None
        try:
            error_body = response.json()
        except Exception:
            pass

        message: str = (
            error_body.get("message", f"HTTP {response.status_code}")
            if error_body
            else f"HTTP {response.status_code}"
        )

        status_code = response.status_code

        if status_code in (401, 403):
            raise AuthenticationError(message)
        if status_code == 429:
            raise RateLimitError(message)
        if status_code == 422 or (status_code == 400 and error_body and error_body.get("errors")):
            raise ValidationError(message, error_body.get("errors") if error_body else None)

        api_status: str | None = error_body.get("status") if error_body else None
        raise DecodoError(message, status_code, api_status)

    def post(self, path: str, body: Any) -> Any:
        return self.request("POST", path, body)

    def get(self, path: str, query: dict[str, str] | None = None) -> Any:
        if query:
            qs = urlencode(query)
            if qs:
                return self.request("GET", f"{path}?{qs}")
        return self.request("GET", path)
