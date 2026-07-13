from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from decodo.schema.constants import (
    DEFAULT_IR_BASE,
    DEFAULT_IR_LIST_URL,
    DEFAULT_IR_PREFIX,
)
from decodo.schema.resolve_latest_ir import resolve_latest_ir


def _make_response(body: Any, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.is_success = 200 <= status < 300
    mock.json.return_value = body
    return mock


class TestResolveLatestIr:
    def test_picks_highest_semver_and_builds_ir_url(self) -> None:
        captured_url: list[str] = []

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            captured_url.append(url)
            return _make_response({
                "items": [
                    {"name": f"{DEFAULT_IR_PREFIX}1.0.0.json"},
                    {"name": f"{DEFAULT_IR_PREFIX}2.1.0.json"},
                    {"name": f"{DEFAULT_IR_PREFIX}2.0.9.json"},
                ]
            })

        with patch("httpx.get", side_effect=fake_get):
            result = resolve_latest_ir()

        assert captured_url[0] == DEFAULT_IR_LIST_URL
        assert result == {
            "version": "2.1.0",
            "url": f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}2.1.0.json",
        }

    def test_throws_when_no_versioned_ir_objects_found(self) -> None:
        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            return _make_response({"items": []})

        with patch("httpx.get", side_effect=fake_get):
            with pytest.raises(RuntimeError, match="No versioned IR objects found"):
                resolve_latest_ir()
