from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from decodo.api.web_scraping_api import DATA_API_ROUTES, SCRAPER_API_ROUTES, WebScrapingApi
from decodo.errors import (
    AuthenticationError,
    DecodoError,
    JobTimeoutError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.remote_schema import RemoteSchema

IR = json.loads((Path(__file__).parent / "schema" / "fixtures" / "flows_ir.json").read_text(encoding="utf-8"))


def _api(ir: dict[str, Any] = IR) -> tuple[WebScrapingApi, MagicMock]:
    http = MagicMock()
    targets = ir["apis"]["webScrapingApi"]["targets"]
    parameter_schemas = {name: target["parameter_schema"] for name, target in targets.items()}
    return WebScrapingApi(http, RemoteSchema(ir, parameter_schemas), DATA_API_ROUTES), http  # type: ignore[arg-type]


class TestCallFlow:
    @pytest.mark.parametrize(
        ("flow", "path", "body"),
        [
            ("search", "/v1/search", {"query": "decodo"}),
            ("map", "/v1/map", {"url": "https://example.com"}),
            ("scrape", "/v1/scrape", {"target": "universal", "url": "https://example.com"}),
        ],
    )
    def test_sends_the_request_the_ir_describes_and_returns_the_response(
        self, flow: str, path: str, body: dict[str, Any]
    ) -> None:
        api, http = _api()
        http.request.return_value = {"ok": True}

        assert api.flows.call(flow, body) == {"ok": True}
        http.request.assert_called_once_with("POST", path, body)

    def test_a_body_the_endpoint_schema_refuses_is_not_sent(self) -> None:
        api, http = _api()

        with pytest.raises(ValidationError):
            api.flows.call("map", {"url": "https://example.com", "sitemap": "sometimes"})
        http.request.assert_not_called()

    def test_a_scrape_body_is_checked_against_its_target(self) -> None:
        api, http = _api()

        with pytest.raises(ValidationError):
            api.flows.call("scrape", {"target": "universal", "headless": "pdf"})
        http.request.assert_not_called()


class TestJobFlow:
    def test_crawl_runs_from_start_to_paged_results(self) -> None:
        api, http = _api()
        http.request.side_effect = [
            {"crawl_id": "c1", "status": "pending"},
            {"crawl_id": "c1", "status": "pending"},
            {"crawl_id": "c1", "status": "truncated"},
            {
                "crawl_id": "c1",
                "url": [{"url": "https://example.com/1"}],
                "next": "https://other.host/v1/crawl/c1?cursor=2",
            },
        ]
        http.get.return_value = {"crawl_id": "c1", "url": [{"url": "https://example.com/2"}]}

        with patch("decodo.api.flows.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 1.0]
            started = api.flows.start("crawl", {"url": "https://example.com"})
            status = api.flows.wait("crawl", started["crawl_id"], poll_interval=4, timeout=60)
            pages = api.flows.results("crawl", "c1")

        assert status["status"] == "truncated"
        assert not api.flows.has_failed("crawl", status)
        assert pages == [{"url": "https://example.com/1"}, {"url": "https://example.com/2"}]
        assert http.request.call_args_list == [
            call("POST", "/v1/crawl", {"url": "https://example.com"}),
            call("GET", "/v1/crawl/c1/status", None),
            call("GET", "/v1/crawl/c1/status", None),
            call("GET", "/v1/crawl/c1?type=content", None),
        ]
        http.get.assert_called_once_with("/v1/crawl/c1?cursor=2")
        assert fake_time.sleep.call_args_list == [call(4)]

    def test_task_runs_from_start_to_results_with_its_own_fields(self) -> None:
        api, http = _api()
        results = {"results": [{"content": "<html>", "status_code": 200}]}
        http.request.side_effect = [{"id": "777", "status": "pending"}, {"id": "777", "status": "done"}, results]

        started = api.flows.start("task", {"target": "universal", "url": "https://example.com"})
        status = api.flows.wait("task", started["id"])

        assert api.flows.results("task", "777") == results
        assert status == {"id": "777", "status": "done"}
        assert http.request.call_args_list == [
            call("POST", "/v1/task", {"target": "universal", "url": "https://example.com"}),
            call("GET", "/v1/task/777", None),
            call("GET", "/v1/task/777/results", None),
        ]

    @pytest.mark.parametrize(("flow", "state"), [("crawl", "faulted"), ("crawl", "cancelled"), ("task", "faulted")])
    def test_a_failed_job_is_returned_and_recognised_not_raised(self, flow: str, state: str) -> None:
        api, http = _api()
        http.request.return_value = {"status": state}

        status = api.flows.wait(flow, "j1")

        assert api.flows.has_failed(flow, status)
        assert not api.flows.is_pending(flow, status)

    def test_wait_raises_at_the_timeout_with_the_flow_and_job_id(self) -> None:
        api, http = _api()
        http.request.return_value = {"status": "pending"}

        with patch("decodo.api.flows.time") as fake_time:
            fake_time.monotonic.side_effect = [0.0, 5.0, 10.0]
            with pytest.raises(JobTimeoutError) as raised:
                api.flows.wait("task", "777", poll_interval=5, timeout=10)

        assert (raised.value.flow, raised.value.job_id) == ("task", "777")
        assert fake_time.sleep.call_args_list == [call(5)]

    @pytest.mark.parametrize(("published", "slept"), [(2, 2.0), (0, 5.0), ("fast", 5.0), (None, 5.0)])
    def test_wait_polls_at_the_interval_the_ir_gives_the_flow(self, published: Any, slept: float) -> None:
        ir = copy.deepcopy(IR)
        if published is None:
            del ir["flows"]["task"]["pollSeconds"]
        else:
            ir["flows"]["task"]["pollSeconds"] = published
        api, http = _api(ir)
        http.request.side_effect = [{"status": "pending"}, {"status": "done"}]

        with patch("decodo.api.flows.time") as fake_time:
            api.flows.wait("task", "777")

        assert fake_time.sleep.call_args_list == [call(slept)]

    def test_wait_rejects_a_non_positive_poll_interval(self) -> None:
        api, _ = _api()

        with pytest.raises(ValueError):
            api.flows.wait("crawl", "c1", poll_interval=0)

    def test_cancel_posts_to_the_cancel_endpoint(self) -> None:
        api, http = _api()
        http.request.return_value = {"crawl_id": "c1", "status": "cancelled"}

        assert api.flows.cancel("crawl", "c1")["status"] == "cancelled"
        http.request.assert_called_once_with("POST", "/v1/crawl/c1/cancel", None)

    def test_a_flow_without_a_cancel_endpoint_cannot_be_cancelled(self) -> None:
        api, http = _api()

        with pytest.raises(ValueError, match="cannot be cancelled"):
            api.flows.cancel("task", "777")
        http.request.assert_not_called()

    def test_a_start_body_the_schema_refuses_is_not_sent(self) -> None:
        api, http = _api()

        with pytest.raises(ValidationError):
            api.flows.start("crawl", {"url": "https://example.com", "output": "pdf"})
        http.request.assert_not_called()


class TestBatchFlow:
    def test_returns_the_jobs_it_started_which_follow_the_task_flow(self) -> None:
        api, http = _api()
        body = {"target": "universal", "url": ["https://example.com/1", "https://example.com/2"]}
        started = [{"id": "1", "status": "pending"}, {"id": "2", "status": "pending"}]
        http.request.return_value = {"id": 9, "queries": started}

        jobs = api.flows.start_batch("task_batch", body)

        assert [job["id"] for job in jobs] == ["1", "2"]
        assert all(api.flows.is_pending("task", job) for job in jobs)
        http.request.assert_called_once_with("POST", "/v1/task/batch", body)

    def test_returns_nothing_when_no_job_was_accepted(self) -> None:
        api, http = _api()
        http.request.return_value = {"queries": []}

        assert api.flows.start_batch("task_batch", {"target": "universal", "url": []}) == []


class TestFlowLookup:
    def test_an_unknown_flow_is_an_error(self) -> None:
        api, _ = _api()

        with pytest.raises(ValueError, match="Unknown flow 'nope'"):
            api.flows.call("nope", {})

    def test_a_flow_of_another_pattern_is_an_error(self) -> None:
        api, _ = _api()

        with pytest.raises(ValueError, match="is a job flow, not a call flow"):
            api.flows.call("crawl", {})

    def test_an_ir_that_predates_flows_is_an_error(self) -> None:
        api, _ = _api({key: value for key, value in IR.items() if key != "flows"})

        with pytest.raises(ValueError, match="Unknown flow"):
            api.flows.call("search", {"query": "q"})

    def test_flows_need_an_api_key(self) -> None:
        api = WebScrapingApi(MagicMock(), BundledSchema.shared, SCRAPER_API_ROUTES)

        with pytest.raises(ValueError, match="require an API key"):
            api.flows.call("search", {"query": "q"})


class TestSchemaAccess:
    def test_exposes_flows_endpoints_and_surfaces(self) -> None:
        api, _ = _api()
        schema = api._schema

        assert schema.get_flow("crawl")["idField"] == "crawl_id"  # type: ignore[attr-defined]
        assert schema.get_operation("getTask") == {"method": "GET", "path": "/v1/task/{id}"}  # type: ignore[attr-defined]
        assert schema.get_surface("google-adk-python")["tools"][0]["flow"] == "search"  # type: ignore[attr-defined]
        assert schema.get_flow("nope") is None  # type: ignore[attr-defined]


class TestRequestsStayOnTheApiHost:
    @pytest.mark.parametrize("path", ["@evil.example/v1/x", "//evil.example/v1/x", "https://evil.example/x", ""])
    def test_a_path_that_could_name_another_host_is_refused(self, path: str) -> None:
        ir = copy.deepcopy(IR)
        ir["operations"]["runSearch"]["path"] = path
        api, http = _api(ir)

        with pytest.raises(ValueError, match="not a path on the API host"):
            api.flows.call("search", {"query": "q"})
        http.request.assert_not_called()

    @pytest.mark.parametrize(
        ("job_id", "sent"),
        [
            ("../task/batch?x=", "/v1/crawl/..%2Ftask%2Fbatch%3Fx%3D/cancel"),
            ("c1/status", "/v1/crawl/c1%2Fstatus/cancel"),
            (42, "/v1/crawl/42/cancel"),
        ],
    )
    def test_a_job_id_cannot_reach_another_endpoint(self, job_id: Any, sent: str) -> None:
        api, http = _api()
        http.request.return_value = {}

        api.flows.cancel("crawl", job_id)

        http.request.assert_called_once_with("POST", sent, None)

    def test_an_empty_job_id_is_refused(self) -> None:
        api, http = _api()

        with pytest.raises(ValueError, match="needs a job id"):
            api.flows.status("crawl", "")
        http.request.assert_not_called()

    def test_a_job_operation_without_a_place_for_the_id_is_refused(self) -> None:
        ir = copy.deepcopy(IR)
        ir["operations"]["getCrawlStatus"]["path"] = "/v1/crawl/status"
        api, http = _api(ir)

        with pytest.raises(ValueError, match="needs a job id"):
            api.flows.status("crawl", "c1")
        http.request.assert_not_called()

    def test_a_next_link_that_could_name_another_host_is_refused(self) -> None:
        api, http = _api()
        http.request.return_value = {"url": [], "next": "@evil.example/v1/crawl/c1"}

        with pytest.raises(ValueError, match="not a path on the API host"):
            api.flows.results("crawl", "c1")
        http.get.assert_not_called()


class TestResultsEdges:
    def test_results_that_are_not_ready_come_back_empty(self) -> None:
        api, http = _api()
        http.request.return_value = None

        assert api.flows.results("task", "777") is None
        assert api.flows.results("crawl", "c1") == []

    def test_reading_stops_once_max_items_is_reached(self) -> None:
        api, http = _api()
        http.request.return_value = {"url": [{"url": "1"}, {"url": "2"}], "next": "/v1/crawl/c1?cursor=2"}
        http.get.return_value = {"url": [{"url": "3"}], "next": "/v1/crawl/c1?cursor=3"}

        assert len(api.flows.results("crawl", "c1", max_items=3)) == 3
        http.get.assert_called_once_with("/v1/crawl/c1?cursor=2")


class TestIrPublishedLater:
    @pytest.mark.parametrize("value", ["x", ["x"], 3, None, {"crawl": "x"}])
    def test_sections_of_the_wrong_type_are_dropped_not_fatal(self, value: Any) -> None:
        ir = {**IR, "flows": value, "surfaces": value, "operations": value}
        api, _ = _api(ir)

        assert api._schema.get_surface("google-adk-python") is None  # type: ignore[attr-defined]
        with pytest.raises(ValueError, match="Unknown flow"):
            api.flows.call("search", {"query": "q"})


class TestKeyCheck:
    def test_sends_the_request_the_ir_gives(self) -> None:
        api, http = _api()

        api.flows.check_key()

        http.request.assert_called_once_with(
            "POST", "/v1/scrape", {"target": "universal", "url": "https://does-not-exist.decodo.com"}
        )

    @pytest.mark.parametrize("error", [DecodoError("target unreachable", 613), DecodoError("bad gateway", 502)])
    def test_another_answer_means_the_key_was_accepted(self, error: Exception) -> None:
        api, http = _api()
        http.request.side_effect = error

        api.flows.check_key()

    @pytest.mark.parametrize("error", [AuthenticationError(), RateLimitError(), TimeoutError()])
    def test_a_rejected_or_unproven_key_raises(self, error: Exception) -> None:
        api, http = _api()
        http.request.side_effect = error

        with pytest.raises(type(error)):
            api.flows.check_key()

    def test_an_ir_without_a_key_check_is_an_error(self) -> None:
        api, _ = _api({key: value for key, value in IR.items() if key != "keyCheck"})

        with pytest.raises(ValueError, match="no key check"):
            api.flows.check_key()
