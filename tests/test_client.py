from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from decodo.client import DecodoClient, DecodoConfig, WebScrapingApiConfig

SCRAPE_PARAMS = {"target": "universal", "url": "https://example.com"}


def _make_response(body: Any, status: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status
    mock.is_success = 200 <= status < 300
    mock.json.return_value = body
    return mock


class TestTransportSelection:
    def _collect_urls(self, config: WebScrapingApiConfig) -> list[str]:
        urls: list[str] = []

        def fake_request(method: str, url: str, **kwargs: Any) -> MagicMock:
            urls.append(url)
            return _make_response({"results": []})

        with patch("httpx.request", side_effect=fake_request):
            client = DecodoClient(DecodoConfig(web_scraping_api=config))
            client.web_scraping_api.scrape(SCRAPE_PARAMS)
            client.web_scraping_api.get_status("task-1")

        return urls

    def test_routes_a_token_to_scraper_api_over_v2_v3(self) -> None:
        assert self._collect_urls(WebScrapingApiConfig(token="test-token")) == [
            "https://scraper-api.decodo.com/v2/scrape",
            "https://scraper-api.decodo.com/v3/task/task-1",
        ]

    def test_routes_an_api_key_to_data_decodo_com_over_v1(self) -> None:
        assert self._collect_urls(WebScrapingApiConfig(api_key="test-key")) == [
            "https://data.decodo.com/v1/scrape",
            "https://data.decodo.com/v1/task/task-1",
        ]

    def test_raises_when_both_token_and_api_key_are_provided(self) -> None:
        with pytest.raises(ValueError, match="either token or api_key"):
            DecodoClient(
                DecodoConfig(
                    web_scraping_api=WebScrapingApiConfig(
                        token="test-token", api_key="test-key"
                    )
                )
            )

    def test_raises_when_neither_token_nor_api_key_is_provided(self) -> None:
        with pytest.raises(ValueError, match="web_scraping_api requires"):
            DecodoClient(DecodoConfig(web_scraping_api=WebScrapingApiConfig()))

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_raises_when_the_only_credential_is_blank(self, blank: str) -> None:
        with pytest.raises(ValueError, match="web_scraping_api requires"):
            DecodoClient(DecodoConfig(web_scraping_api=WebScrapingApiConfig(token=blank)))
        with pytest.raises(ValueError, match="web_scraping_api requires"):
            DecodoClient(DecodoConfig(web_scraping_api=WebScrapingApiConfig(api_key=blank)))

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_credential_does_not_shadow_the_other_one(self, blank: str) -> None:
        assert self._collect_urls(WebScrapingApiConfig(token=blank, api_key="test-key")) == [
            "https://data.decodo.com/v1/scrape",
            "https://data.decodo.com/v1/task/task-1",
        ]
        assert self._collect_urls(WebScrapingApiConfig(token="test-token", api_key=blank)) == [
            "https://scraper-api.decodo.com/v2/scrape",
            "https://scraper-api.decodo.com/v3/task/task-1",
        ]
