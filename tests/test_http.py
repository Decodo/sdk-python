from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import httpx

from decodo.http import ApiKeyAuth, BasicAuth, HttpClient, HttpClientConfig

BASE_CONFIG = HttpClientConfig(
    base_url="https://api.test",
    auth=BasicAuth(type="basic", token="test-token"),
    timeout_ms=5000,
)


def _make_response(body: Any, status: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status
    mock.is_success = 200 <= status < 300
    mock.json.return_value = body
    return mock


class TestHttpClientIntegrationHeader:
    def test_sends_sdk_python_by_default(self) -> None:
        captured: dict[str, Any] = {}

        def fake_request(method: str, url: str, **kwargs: Any) -> MagicMock:
            captured["headers"] = kwargs.get("headers", {})
            return _make_response({"ok": True})

        with patch("httpx.request", side_effect=fake_request):
            client = HttpClient(BASE_CONFIG)
            client.get("/v3/task/1")

        assert captured["headers"]["x-integration"] == "sdk-python"

    def test_sends_custom_integration_header(self) -> None:
        captured: dict[str, Any] = {}

        def fake_request(method: str, url: str, **kwargs: Any) -> MagicMock:
            captured["headers"] = kwargs.get("headers", {})
            return _make_response({"ok": True})

        with patch("httpx.request", side_effect=fake_request):
            client = HttpClient(
                HttpClientConfig(
                    base_url="https://api.test",
                    auth=BasicAuth(type="basic", token="test-token"),
                    timeout_ms=5000,
                    integration_header="cli",
                )
            )
            client.get("/v3/task/1")

        assert captured["headers"]["x-integration"] == "cli"


class TestHttpClientAuthHeader:
    def _captured_headers(self, config: HttpClientConfig) -> dict[str, str]:
        captured: dict[str, dict[str, str]] = {}

        def fake_request(method: str, url: str, **kwargs: Any) -> MagicMock:
            captured["headers"] = kwargs.get("headers", {})
            return _make_response({"ok": True})

        with patch("httpx.request", side_effect=fake_request):
            HttpClient(config).get("/v3/task/1")

        return captured["headers"]

    def test_sends_basic_auth_for_a_token(self) -> None:
        headers = self._captured_headers(BASE_CONFIG)

        assert headers["Authorization"] == "Basic test-token"

    def test_sends_bearer_auth_for_an_api_key(self) -> None:
        headers = self._captured_headers(
            HttpClientConfig(
                base_url="https://api.test",
                auth=ApiKeyAuth(type="apiKey", api_key="test-key"),
                timeout_ms=5000,
            )
        )

        assert headers["Authorization"] == "Bearer test-key"
