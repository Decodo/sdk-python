from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from decodo.api.web_scraping_api import WebScrapingApi
from decodo.errors import ValidationError
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.types import DecodoSchema, TargetMeta


class _StrictSchema:
    """Schema that only accepts google_search with non-empty query."""

    def get_request_schema(self, target: str) -> dict[str, Any] | None:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "const": "google_search"},
                "query": {"type": "string", "minLength": 1},
            },
            "required": ["target", "query"],
        }

    def list_targets(self) -> list[str]:
        return []

    def get_target_meta(self, target: str) -> TargetMeta | None:
        return None

    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None:
        return None

    def get_shared_parameters(self) -> dict[str, Any]:
        return {}

    @property
    def version(self) -> str | None:
        return None


def _make_http_mock() -> MagicMock:
    mock = MagicMock()
    mock.post.return_value = {"results": []}
    return mock


class TestWebScrapingApiValidation:
    def test_throws_validation_error_before_http_when_schema_rejects(self) -> None:
        http = _make_http_mock()
        api = WebScrapingApi(http, _StrictSchema())  # type: ignore[arg-type]

        with pytest.raises(ValidationError):
            api.scrape({"target": "google_search", "query": ""})

        http.post.assert_not_called()

    def test_calls_http_when_params_pass_schema_validation(self) -> None:
        http = _make_http_mock()
        api = WebScrapingApi(http, _StrictSchema())  # type: ignore[arg-type]

        api.scrape({"target": "google_search", "query": "coffee"})

        http.post.assert_called_once()

    def test_validates_bundled_google_search_payloads(self) -> None:
        http = _make_http_mock()
        api = WebScrapingApi(http, BundledSchema.shared)

        api.scrape({"target": "google_search", "query": "coffee"})

        http.post.assert_called_once()
