from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from decodo.schema.constants import (
    DEFAULT_IR_BASE,
    DEFAULT_IR_LIST_URL,
    DEFAULT_IR_PREFIX,
)
from decodo.schema.remote_schema import RemoteSchema
from decodo.schema.types import CachedIr, RemoteIr, RemoteSchemaLoadOptions

MINIMAL_IR_PATH = Path(__file__).parent / "fixtures" / "minimal_ir.json"

with open(MINIMAL_IR_PATH, encoding="utf-8") as _f:
    _MINIMAL_IR: RemoteIr = json.load(_f)

IR_URL = "https://example.test/decodo-ir-v1.0.0.json"


def _clone_ir(version: str) -> RemoteIr:
    ir = dict(_MINIMAL_IR)
    ir["version"] = version
    return ir  # type: ignore[return-value]


def _make_response(body: Any, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.is_success = 200 <= status < 300
    mock.json.return_value = body
    return mock


def _write_cached_ir(cache_path: str, cached: CachedIr) -> None:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cached, f, indent=2)


@contextmanager
def _temp_cache_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory(prefix="decodo-schema-test-") as d:
        yield os.path.join(d, "decodo.ir.json")


class TestRemoteSchemaLoad:
    def test_cold_load_fetches_ir_writes_cache_and_exposes_introspection(self) -> None:
        call_count = 0

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            assert url == IR_URL
            return _make_response(_MINIMAL_IR)

        with _temp_cache_dir() as cache_path:
            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(
                    RemoteSchemaLoadOptions(url=IR_URL, cache_path=cache_path)
                )

            assert call_count == 1
            assert schema.version == "1.0.0"
            assert schema.list_targets() == ["google_search"]
            target_meta = schema.get_target_meta("google_search")
            assert target_meta is not None and "query" in target_meta["parameters"]
            assert "GEOLOCATION_NAME" in schema.get_shared_parameters()

            with open(cache_path, encoding="utf-8") as f:
                cached: CachedIr = json.load(f)
            assert cached["resolved_url"] == IR_URL
            assert cached["ir"]["version"] == "1.0.0"

    def test_uses_cache_when_ttl_is_fresh(self) -> None:
        import time

        call_count = 0

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            return _make_response(_MINIMAL_IR)

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(
                cache_path,
                CachedIr(
                    fetched_at=int(time.time() * 1000),
                    resolved_url=IR_URL,
                    ir=_MINIMAL_IR,
                ),
            )

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(
                    RemoteSchemaLoadOptions(url=IR_URL, cache_path=cache_path, ttl_ms=60_000)
                )

            assert call_count == 0
            assert schema.version == "1.0.0"

    def test_uses_stale_cache_when_resolved_version_is_unchanged(self) -> None:
        import time

        latest_url = f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}2.1.0.json"
        call_count = 0

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            if url == DEFAULT_IR_LIST_URL:
                return _make_response({
                    "items": [{"name": f"{DEFAULT_IR_PREFIX}2.1.0.json"}]
                })
            raise AssertionError(f"Unexpected fetch: {url}")

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(
                cache_path,
                CachedIr(
                    fetched_at=int(time.time() * 1000) - 60_000,
                    resolved_url=latest_url,
                    ir=_clone_ir("2.1.0"),
                ),
            )

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(
                    RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=1_000)
                )

            assert call_count == 1
            assert schema.version == "2.1.0"

    def test_refetches_when_stale_cache_version_differs_from_latest(self) -> None:
        import time

        latest_url = f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}2.1.0.json"
        call_count = 0

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            if url == DEFAULT_IR_LIST_URL:
                return _make_response({
                    "items": [{"name": f"{DEFAULT_IR_PREFIX}2.1.0.json"}]
                })
            if url == latest_url:
                return _make_response(_clone_ir("2.1.0"))
            raise AssertionError(f"Unexpected fetch: {url}")

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(
                cache_path,
                CachedIr(
                    fetched_at=int(time.time() * 1000) - 60_000,
                    resolved_url=latest_url,
                    ir=_clone_ir("1.0.0"),
                ),
            )

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(
                    RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=1_000)
                )

            assert call_count == 2
            assert schema.version == "2.1.0"

    def test_refetches_when_cache_url_does_not_match_requested_url(self) -> None:
        import time

        other_url = "https://example.test/decodo-ir-v9.9.9.json"
        call_count = 0

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            assert url == other_url
            return _make_response(_clone_ir("9.9.9"))

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(
                cache_path,
                CachedIr(
                    fetched_at=int(time.time() * 1000),
                    resolved_url=IR_URL,
                    ir=_MINIMAL_IR,
                ),
            )

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(
                    RemoteSchemaLoadOptions(url=other_url, cache_path=cache_path, ttl_ms=60_000)
                )

            assert call_count == 1
            assert schema.version == "9.9.9"


class TestRemoteSchemaDataApi:
    def test_exposes_data_api_endpoint_request_schemas(self) -> None:
        schema = RemoteSchema(_MINIMAL_IR, {})

        assert schema.get_endpoint_request_schema("mapSite") == {
            "type": "object",
            "required": ["url"],
            "properties": {"url": {"type": "string"}, "limit": {"type": "integer"}},
        }

    def test_returns_none_when_the_ir_predates_the_data_api_section(self) -> None:
        ir: Any = {"version": "0.9.0", "apis": {"webScrapingApi": _MINIMAL_IR["apis"]["webScrapingApi"]}}
        schema = RemoteSchema(ir, {})

        assert schema.get_endpoint_request_schema("runSearch") is None


def _latest_cache(version: str = "1.0.0", *, age_ms: int = 0) -> CachedIr:
    import time

    return CachedIr(
        fetched_at=int(time.time() * 1000) - age_ms,
        resolved_url=f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}{version}.json",
        ir=_clone_ir(version),
    )


class TestRemoteSchemaOffline:
    def test_fresh_cache_of_the_latest_ir_is_used_without_any_request(self) -> None:
        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache())

            with patch("httpx.get", side_effect=AssertionError("no request expected")):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "1.0.0"

    def test_stale_cache_is_used_when_the_versions_cannot_be_listed(self) -> None:
        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache(age_ms=120_000))

            with patch("httpx.get", side_effect=httpx.ConnectError("offline")):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "1.0.0"

    def test_stale_cache_is_used_when_the_new_ir_cannot_be_fetched(self) -> None:
        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            if url == DEFAULT_IR_LIST_URL:
                return _make_response({"items": [{"name": f"{DEFAULT_IR_PREFIX}2.0.0.json"}]})
            return _make_response({}, status=503)

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache(age_ms=120_000))

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "1.0.0"

    def test_raises_when_offline_with_no_cache(self) -> None:
        with _temp_cache_dir() as cache_path:
            with patch("httpx.get", side_effect=httpx.ConnectError("offline")):
                with pytest.raises(httpx.ConnectError):
                    RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path))

    def test_cache_of_another_url_is_not_used_when_the_requested_url_fails(self) -> None:
        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache())

            with patch("httpx.get", side_effect=httpx.ConnectError("offline")):
                with pytest.raises(httpx.ConnectError):
                    RemoteSchema.load(RemoteSchemaLoadOptions(url=IR_URL, cache_path=cache_path))


class TestRemoteSchemaCacheOwnership:
    def test_cache_of_a_pinned_url_is_not_served_as_the_latest_ir(self) -> None:
        import time

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            if url == DEFAULT_IR_LIST_URL:
                return _make_response({"items": [{"name": f"{DEFAULT_IR_PREFIX}2.0.0.json"}]})
            return _make_response(_clone_ir("2.0.0"))

        with _temp_cache_dir() as cache_path:
            pinned = CachedIr(fetched_at=int(time.time() * 1000), resolved_url=IR_URL, ir=_clone_ir("0.9.0"))
            _write_cached_ir(cache_path, pinned)

            with patch("httpx.get", side_effect=fake_get):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "2.0.0"

    def test_cache_of_a_pinned_url_is_not_used_offline_for_the_latest_ir(self) -> None:
        import time

        with _temp_cache_dir() as cache_path:
            pinned = CachedIr(fetched_at=int(time.time() * 1000), resolved_url=IR_URL, ir=_clone_ir("0.9.0"))
            _write_cached_ir(cache_path, pinned)

            with patch("httpx.get", side_effect=httpx.ConnectError("offline")):
                with pytest.raises(httpx.ConnectError):
                    RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

    def test_a_stale_cache_confirmed_as_latest_is_fresh_again(self) -> None:
        requests: list[str] = []

        def fake_get(url: str, **kwargs: Any) -> MagicMock:
            requests.append(url)
            return _make_response({"items": [{"name": f"{DEFAULT_IR_PREFIX}1.0.0.json"}]})

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache(age_ms=120_000))
            options = RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000)

            with patch("httpx.get", side_effect=fake_get):
                RemoteSchema.load(options)
                RemoteSchema.load(options)

            assert requests == [DEFAULT_IR_LIST_URL]

    def test_a_stale_cache_confirmed_as_latest_loads_when_it_cannot_be_rewritten(self) -> None:
        listing = _make_response({"items": [{"name": f"{DEFAULT_IR_PREFIX}1.0.0.json"}]})

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache(age_ms=120_000))

            with (
                patch("httpx.get", return_value=listing),
                patch("decodo.schema.remote_schema._write_cached_ir", side_effect=PermissionError("read-only")),
            ):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "1.0.0"

    def test_cached_copy_is_used_when_the_listing_is_not_json(self) -> None:
        broken = _make_response(None)
        broken.json.side_effect = ValueError("not json")

        with _temp_cache_dir() as cache_path:
            _write_cached_ir(cache_path, _latest_cache(age_ms=120_000))

            with patch("httpx.get", return_value=broken), pytest.warns(RuntimeWarning, match="cached copy"):
                schema = RemoteSchema.load(RemoteSchemaLoadOptions(cache_path=cache_path, ttl_ms=60_000))

            assert schema.version == "1.0.0"
