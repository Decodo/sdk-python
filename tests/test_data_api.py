from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from decodo.api.web_scraping_api import DATA_API_ROUTES, SCRAPER_API_ROUTES, WebScrapingApi
from decodo.errors import (
    CrawlError,
    CrawlInterruptedError,
    CrawlTimeoutError,
    DecodoError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.types import TargetMeta


class _NoSchema:
    """Schema with no endpoint schemas, so validation is skipped."""

    def get_request_schema(self, target: str) -> dict[str, Any] | None:
        return None

    def list_targets(self) -> list[str]:
        return []

    def get_target_meta(self, target: str) -> TargetMeta | None:
        return None

    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None:
        return None

    def get_shared_parameters(self) -> dict[str, Any]:
        return {}

    def get_endpoint_request_schema(self, endpoint: str) -> dict[str, Any] | None:
        return None

    @property
    def version(self) -> str | None:
        return None


def _data_api(http: MagicMock | None = None) -> tuple[WebScrapingApi, MagicMock]:
    http = http or MagicMock()
    return WebScrapingApi(http, _NoSchema(), DATA_API_ROUTES), http


class TestSearchAndMap:
    def test_search_posts_to_v1_search_and_returns_the_body(self) -> None:
        api, http = _data_api()
        http.post.return_value = {"status": "done", "organic": []}

        result = api.search({"query": "coffee", "page": 1})

        http.post.assert_called_once_with("/v1/search", {"query": "coffee", "page": 1})
        assert result == {"status": "done", "organic": []}

    def test_map_posts_to_v1_map_and_returns_the_body(self) -> None:
        api, http = _data_api()
        body: dict[str, Any] = {"results": [{"content": {"links": [{"url": "https://example.com/a"}]}}]}
        http.post.return_value = body

        result = api.map({"url": "https://example.com", "limit": 10})

        http.post.assert_called_once_with("/v1/map", {"url": "https://example.com", "limit": 10})
        assert result == body


class TestBasicTokenRejected:
    @pytest.mark.parametrize(
        "call",
        [
            lambda api: api.search({"query": "coffee"}),
            lambda api: api.map({"url": "https://example.com"}),
            lambda api: api.start_crawl({"url": "https://example.com"}),
            lambda api: api.get_crawl_status("crawl-1"),
            lambda api: api.get_crawl_results("crawl-1"),
            lambda api: api.cancel_crawl("crawl-1"),
            lambda api: api.crawl({"url": "https://example.com"}),
        ],
        ids=["search", "map", "start_crawl", "get_crawl_status", "get_crawl_results", "cancel_crawl", "crawl"],
    )
    def test_raises_saying_an_api_key_is_required_without_calling_http(self, call: Any) -> None:
        http = MagicMock()
        api = WebScrapingApi(http, _NoSchema(), SCRAPER_API_ROUTES)

        with pytest.raises(ValueError, match="requires an API key"):
            call(api)

        http.post.assert_not_called()
        http.get.assert_not_called()


def _page(url: str, **extra: Any) -> dict[str, Any]:
    return {"url": url, "status": "done", "depth": 0, **extra}


class TestCrawlLowLevel:
    def test_start_crawl_posts_to_v1_crawl_and_returns_the_body(self) -> None:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}

        result = api.start_crawl({"url": "https://example.com", "limit": 5})

        http.post.assert_called_once_with("/v1/crawl", {"url": "https://example.com", "limit": 5})
        assert result == {"crawl_id": "crawl-1", "status": "pending"}

    def test_get_crawl_status_gets_the_status_route(self) -> None:
        api, http = _data_api()
        http.get.return_value = {"crawl_id": "crawl-1", "status": "pending", "discovered": 3}

        result = api.get_crawl_status("crawl-1")

        http.get.assert_called_once_with("/v1/crawl/crawl-1/status")
        assert result["status"] == "pending"

    def test_cancel_crawl_posts_to_the_cancel_route(self) -> None:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "cancelled"}

        result = api.cancel_crawl("crawl-1")

        http.post.assert_called_once_with("/v1/crawl/crawl-1/cancel", None)
        assert result["status"] == "cancelled"


class TestGetCrawlResults:
    def test_follows_next_until_there_is_none_and_returns_every_page(self) -> None:
        api, http = _data_api()
        http.get.side_effect = [
            {
                "crawl_id": "crawl-1",
                "url": [_page("https://example.com/", content="a")],
                "next": "https://data.decodo.com/v1/crawl/crawl-1?cursor=c1&type=content",
                "total": 3,
            },
            {
                "crawl_id": "crawl-1",
                "url": [_page("https://example.com/b", content="b")],
                "next": "https://data.decodo.com/v1/crawl/crawl-1?cursor=c2&type=content",
            },
            {
                "crawl_id": "crawl-1",
                "url": [_page("https://example.com/c", content="c")],
            },
        ]

        pages = api.get_crawl_results("crawl-1")

        assert [p["url"] for p in pages] == [
            "https://example.com/",
            "https://example.com/b",
            "https://example.com/c",
        ]
        assert [p["content"] for p in pages] == ["a", "b", "c"]
        assert [c.args for c in http.get.call_args_list] == [
            ("/v1/crawl/crawl-1", {"type": "content"}),
            ("/v1/crawl/crawl-1?cursor=c1&type=content",),
            ("/v1/crawl/crawl-1?cursor=c2&type=content",),
        ]

    def test_next_is_requested_against_the_configured_host_not_the_one_in_the_link(self) -> None:
        api, http = _data_api()
        http.get.side_effect = [
            {"crawl_id": "crawl-1", "url": [], "next": "https://other.host.example/v1/crawl/crawl-1?cursor=c1"},
            {"crawl_id": "crawl-1", "url": []},
        ]

        api.get_crawl_results("crawl-1")

        assert http.get.call_args_list[1].args == ("/v1/crawl/crawl-1?cursor=c1",)

    def test_content_false_requests_metadata_only(self) -> None:
        api, http = _data_api()
        http.get.return_value = {"crawl_id": "crawl-1", "url": [_page("https://example.com/")]}

        pages = api.get_crawl_results("crawl-1", content=False)

        http.get.assert_called_once_with("/v1/crawl/crawl-1", None)
        assert len(pages) == 1

    def test_returns_an_empty_list_when_the_crawl_has_no_pages(self) -> None:
        api, http = _data_api()
        http.get.return_value = {"crawl_id": "crawl-1", "url": []}

        assert api.get_crawl_results("crawl-1") == []


class TestCrawl:
    """``crawl()`` starts a crawl, polls its status, then returns every page."""

    def _api_with_statuses(self, statuses: list[str], **status_extra: Any) -> tuple[WebScrapingApi, MagicMock]:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}
        http.get.side_effect = [{"crawl_id": "crawl-1", "status": s, **status_extra} for s in statuses] + [
            {"crawl_id": "crawl-1", "url": [_page("https://example.com/", content="a")]},
        ]
        return api, http

    def test_returns_every_page_of_a_finished_crawl(self) -> None:
        api, http = self._api_with_statuses(["pending", "pending", "done"])

        with patch("decodo.api.web_scraping_api.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 1.0, 2.0, 3.0]
            pages = api.crawl({"url": "https://example.com"}, poll_interval=7)

        assert pages == [_page("https://example.com/", content="a")]
        http.post.assert_called_once_with("/v1/crawl", {"url": "https://example.com"})
        assert [c.args for c in http.get.call_args_list] == [
            ("/v1/crawl/crawl-1/status",),
            ("/v1/crawl/crawl-1/status",),
            ("/v1/crawl/crawl-1/status",),
            ("/v1/crawl/crawl-1", {"type": "content"}),
        ]
        assert fake_time.sleep.call_args_list == [call(7), call(7)]

    def test_a_truncated_crawl_still_returns_its_pages(self) -> None:
        api, _ = self._api_with_statuses(["truncated"], reason="max_duration")

        pages = api.crawl({"url": "https://example.com"})

        assert len(pages) == 1

    def test_timeout_raises_with_the_crawl_id_and_leaves_the_crawl_running(self) -> None:
        api, http = self._api_with_statuses(["pending", "pending", "pending", "pending"])

        with patch("decodo.api.web_scraping_api.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 4.0, 8.0, 12.0]
            with pytest.raises(CrawlTimeoutError, match="crawl-1") as exc_info:
                api.crawl({"url": "https://example.com"}, poll_interval=1, timeout=10)

        assert exc_info.value.crawl_id == "crawl-1"
        assert isinstance(exc_info.value, TimeoutError)
        # Only the start request was posted: nothing cancelled the crawl.
        assert [c.args[0] for c in http.post.call_args_list] == ["/v1/crawl"]

    @pytest.mark.parametrize("status", ["faulted", "cancelled"])
    def test_a_failed_crawl_raises_crawl_error_with_its_status_and_reason(self, status: str) -> None:
        api, http = self._api_with_statuses([status], reason="no_pages_found")

        with pytest.raises(CrawlError, match="crawl-1") as exc_info:
            api.crawl({"url": "https://example.com"})

        err = exc_info.value
        assert isinstance(err, DecodoError)
        assert (err.crawl_id, err.status, err.reason) == ("crawl-1", status, "no_pages_found")
        assert len(http.get.call_args_list) == 1  # no results fetched

    def test_rejects_a_non_positive_poll_interval(self) -> None:
        api, _ = _data_api()

        with pytest.raises(ValueError, match="poll_interval"):
            api.crawl({"url": "https://example.com"}, poll_interval=0)


class TestDataApiValidation:
    """Request bodies are checked against the IR's dataApi request schemas before any HTTP call."""

    def _bundled_api(self) -> tuple[WebScrapingApi, MagicMock]:
        http = MagicMock()
        # Real bodies, so a crawl that slips past validation settles instead of polling forever.
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}
        http.get.return_value = {"crawl_id": "crawl-1", "status": "done", "url": []}
        return WebScrapingApi(http, BundledSchema.shared, DATA_API_ROUTES), http

    @pytest.mark.parametrize(
        ("call", "endpoint"),
        [
            (lambda api: api.search({"page": 1}), "runSearch"),
            (lambda api: api.map({"limit": 3}), "mapSite"),
            (lambda api: api.start_crawl({"limit": 0, "url": "https://example.com"}), "startCrawl"),
            (lambda api: api.crawl({"limit": 0, "url": "https://example.com"}), "startCrawl"),
        ],
        ids=["search", "map", "start_crawl", "crawl"],
    )
    def test_raises_validation_error_before_http_when_the_schema_rejects(self, call: Any, endpoint: str) -> None:
        api, http = self._bundled_api()

        with pytest.raises(ValidationError):
            call(api)

        http.post.assert_not_called()

    def test_valid_bodies_are_sent(self) -> None:
        api, http = self._bundled_api()
        http.post.return_value = {"status": "done"}

        api.search({"query": "coffee", "page": 2})

        http.post.assert_called_once_with("/v1/search", {"query": "coffee", "page": 2})

    def test_skips_validation_when_the_schema_has_no_entry_for_the_endpoint(self) -> None:
        api, http = _data_api()
        http.post.return_value = {}

        api.search({"page": 1})  # would fail the IR schema; _NoSchema has none

        http.post.assert_called_once()


class TestPublicExports:
    def test_data_api_types_and_errors_are_importable_from_decodo(self) -> None:
        import decodo

        for name in [
            "SearchRequest",
            "SearchResponse",
            "MapRequest",
            "MapResponse",
            "CrawlRequest",
            "CrawlResponse",
            "CrawlStatusResponse",
            "CrawlStatus",
            "CrawlPage",
            "CrawlPagesResponse",
            "CrawlError",
            "CrawlInterruptedError",
            "CrawlTimeoutError",
        ]:
            assert name in decodo.__all__, name
            getattr(decodo, name)


class TestCrawlTimeoutPrecision:
    def test_raises_at_the_timeout_not_a_poll_interval_later(self) -> None:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}
        http.get.return_value = {"crawl_id": "crawl-1", "status": "pending"}

        with patch("decodo.api.web_scraping_api.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 0.0, 1.0]
            with pytest.raises(CrawlTimeoutError):
                api.crawl({"url": "https://example.com"}, poll_interval=4, timeout=1)

        assert fake_time.sleep.call_args_list == [call(1.0)]

    def test_sleeps_the_full_interval_while_more_than_an_interval_remains(self) -> None:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}
        http.get.side_effect = [
            {"crawl_id": "crawl-1", "status": "pending"},
            {"crawl_id": "crawl-1", "status": "pending"},
            {"crawl_id": "crawl-1", "status": "done"},
            {"crawl_id": "crawl-1", "url": []},
        ]

        with patch("decodo.api.web_scraping_api.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 0.0, 3.0, 6.0]
            api.crawl({"url": "https://example.com"}, poll_interval=3, timeout=10)

        assert fake_time.sleep.call_args_list == [call(3), call(3)]


class TestCrawlInterrupted:
    """Requests made after the crawl started that fail must still name the crawl."""

    def _started_api(self) -> tuple[WebScrapingApi, MagicMock]:
        api, http = _data_api()
        http.post.return_value = {"crawl_id": "crawl-1", "status": "pending"}
        return api, http

    def test_status_error_raises_crawl_interrupted_error_naming_the_crawl(self) -> None:
        api, http = self._started_api()
        original = DecodoError("service unavailable", 503, "failed")
        http.get.side_effect = original

        with pytest.raises(CrawlInterruptedError, match="crawl-1") as exc_info:
            api.crawl({"url": "https://example.com"})

        err = exc_info.value
        assert isinstance(err, DecodoError)
        assert err.crawl_id == "crawl-1"
        assert err.status_code == 503
        assert err.__cause__ is original
        assert "service unavailable" in str(err)
        assert [c.args[0] for c in http.post.call_args_list] == ["/v1/crawl"]

    def test_request_timeout_while_polling_is_wrapped_too(self) -> None:
        api, http = self._started_api()
        http.get.side_effect = TimeoutError("Request to /v1/crawl/crawl-1/status timed out after 180000ms")

        with pytest.raises(CrawlInterruptedError) as exc_info:
            api.crawl({"url": "https://example.com"})

        assert exc_info.value.crawl_id == "crawl-1"
        assert isinstance(exc_info.value.__cause__, TimeoutError)

    def test_results_fetch_error_after_done_is_wrapped_too(self) -> None:
        api, http = self._started_api()
        http.get.side_effect = [
            {"crawl_id": "crawl-1", "status": "done"},
            RateLimitError("results read limit reached, retry in 1s"),
        ]

        with pytest.raises(CrawlInterruptedError) as exc_info:
            api.crawl({"url": "https://example.com"})

        assert exc_info.value.crawl_id == "crawl-1"
        assert exc_info.value.status_code == 429
        assert isinstance(exc_info.value.__cause__, RateLimitError)

    def test_start_failure_is_not_wrapped_because_there_is_no_crawl_yet(self) -> None:
        api, http = _data_api()
        http.post.side_effect = RateLimitError("crawl creation limit reached")

        with pytest.raises(RateLimitError):
            api.crawl({"url": "https://example.com"})
