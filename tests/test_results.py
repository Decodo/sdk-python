from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from decodo.api.results import check_result_rule, read_result
from decodo.errors import ResultError

# The result rules Decodo publishes for the google-adk-python surface, cut from the IR built for 2.6.0.
IR = json.loads((Path(__file__).parent / "schema" / "fixtures" / "flows_ir.json").read_text(encoding="utf-8"))
RULES = {tool["name"]: tool.get("result") for tool in IR["surfaces"]["google-adk-python"]["tools"]}
SCRAPE, SEARCH, MAP, CRAWL = (
    RULES["decodo_scrape"],
    RULES["decodo_search"],
    RULES["decodo_map"],
    RULES["decodo_crawl_results"],
)


def failure(rule: Any, response: Any) -> ResultError:
    with pytest.raises(ResultError) as raised:
        read_result(rule, response)
    return raised.value


class TestPublishedRules:
    def test_scrape_returns_the_page_url_and_content(self) -> None:
        response = {"results": [{"status_code": 200, "url": "https://a.test", "content": "# Title", "task_id": "1"}]}

        assert read_result(SCRAPE, response) == {"url": "https://a.test", "content": "# Title"}

    @pytest.mark.parametrize(
        ("response", "code", "retryable"),
        [
            ({"status": "failed", "message": "target unreachable", "status_code": 612}, "612", True),
            ({"status": "failed", "message": "target unreachable"}, "failed", True),
            ({"results": [{"status_code": 613, "content": "<html>blocked</html>"}]}, "613", True),
            ({"results": [{"status_code": 404, "content": "gone"}]}, "404", False),
            ({"results": [{"status_code": 429, "content": "slow"}]}, "429", True),
            ({"results": []}, "empty_response", False),
            ({}, "empty_response", False),
            ({"results": [{"status_code": 200, "content": ""}]}, "empty_content", False),
            ({"results": [{"status_code": 200}]}, "empty_content", False),
        ],
    )
    def test_scrape_failures_inside_a_successful_response(self, response: Any, code: str, retryable: bool) -> None:
        raised = failure(SCRAPE, response)

        assert (raised.code, raised.retryable) == (code, retryable)

    def test_a_failure_carries_the_message_decodo_gave(self) -> None:
        assert str(failure(SCRAPE, {"status": "failed", "message": "target unreachable"})) == "target unreachable"

    def test_search_returns_everything_but_the_echoed_parameters(self) -> None:
        response = {"organic": [{"rank": 1}], "search_parameters": {"query": "q"}, "url": "https://g.test"}

        assert read_result(SEARCH, response) == {"organic": [{"rank": 1}], "url": "https://g.test"}

    def test_search_failure(self) -> None:
        assert failure(SEARCH, {"status": "failed", "message": "no luck"}).code == "failed"

    def test_map_returns_the_site_url_and_a_flat_list_of_links(self) -> None:
        links = [{"url": "https://a.test/1"}, {"url": "https://a.test/2"}]
        response = {"results": [{"status_code": 200, "url": "https://a.test", "content": {"links": links}}]}

        assert read_result(MAP, response) == {
            "url": "https://a.test",
            "links": ["https://a.test/1", "https://a.test/2"],
        }

    def test_map_failure(self) -> None:
        assert failure(MAP, {"results": [{"status_code": 502, "url": "https://a.test"}]}).retryable is True

    def test_crawl_pages_keep_three_fields_each(self) -> None:
        pages = [{"url": "https://a.test/1", "status": "done", "content": "one", "depth": 1, "task_id": "9"}]

        assert read_result(CRAWL, pages) == [{"url": "https://a.test/1", "status": "done", "content": "one"}]

    def test_every_published_rule_has_the_form_the_reader_understands(self) -> None:
        for rule in RULES.values():
            if rule is not None:
                check_result_rule(rule)


class TestReading:
    def test_no_rule_returns_the_response_as_it_is(self) -> None:
        assert read_result(None, {"a": 1}) == {"a": 1}
        assert read_result({}, [1, 2]) == [1, 2]

    def test_a_missing_field_is_none_and_a_missing_item_field_is_skipped(self) -> None:
        rule = {"fields": {"title": "meta.title", "tags": "tags.*.name"}}

        assert read_result(rule, {"tags": [{"name": "a"}, {"id": 2}]}) == {"title": None, "tags": ["a"]}

    def test_a_response_of_an_unexpected_type_is_no_result_or_passes_through(self) -> None:
        assert failure({"from": "results.0"}, ["x"]).code == "empty_response"
        assert read_result({"omit": ["x"]}, "text") == "text"

    @pytest.mark.parametrize("value", [True, "400", None])
    def test_at_least_only_matches_numbers(self, value: Any) -> None:
        rule = {"failures": [{"path": "status_code", "atLeast": 400}]}

        assert read_result(rule, {"status_code": value}) == {"status_code": value}


class TestRuleForm:
    @pytest.mark.parametrize(
        "rule",
        [
            "x",
            {"failures": "x"},
            {"failures": [{"equals": "failed"}]},
            {"failures": [{"path": "status"}]},
            {"failures": [{"path": "status", "equals": "x", "atLeast": 1}]},
            {"failures": [{"path": "status", "atLeast": "400"}]},
            {"failures": [{"path": "status", "equals": "x", "message": 3}]},
            {"from": 3},
            {"fields": ["url"]},
            {"fields": {"url": 1}},
            {"omit": "x"},
            {"required": [1]},
        ],
    )
    def test_a_rule_of_another_form_is_refused(self, rule: Any) -> None:
        with pytest.raises(TypeError):
            check_result_rule(rule)
