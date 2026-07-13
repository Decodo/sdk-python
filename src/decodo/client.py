from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .api.web_scraping_api import WebScrapingApi
from .http import BasicAuth, HttpClient, HttpClientConfig
from .schema.bundled_schema import BundledSchema
from .schema.types import DecodoSchema

WEB_API_BASE_URL = "https://scraper-api.decodo.com"
DEFAULT_TIMEOUT_MS = 180_000


@dataclass
class WebScrapingApiConfig:
    token: str
    integration_header: str | None = None


@dataclass
class DecodoConfig:
    web_scraping_api: WebScrapingApiConfig | None = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    schema: DecodoSchema | None = None


def _not_configured(namespace: str, hint: str) -> Any:
    raise RuntimeError(f"{namespace} is not configured. {hint}")


class _UnconfiguredWebScrapingApi:
    def __getattr__(self, name: str) -> Any:
        _not_configured(
            "web_scraping_api",
            "Provide web_scraping_api in DecodoConfig.",
        )


class DecodoClient:
    web_scraping_api: WebScrapingApi

    def __init__(self, config: DecodoConfig) -> None:
        timeout_ms = config.timeout_ms
        schema: DecodoSchema = config.schema if config.schema is not None else BundledSchema.shared

        if config.web_scraping_api is not None:
            http = HttpClient(
                HttpClientConfig(
                    base_url=WEB_API_BASE_URL,
                    auth=BasicAuth(type="basic", token=config.web_scraping_api.token),
                    timeout_ms=timeout_ms,
                    integration_header=config.web_scraping_api.integration_header,
                )
            )
            self.web_scraping_api = WebScrapingApi(http, schema)
        else:
            self.web_scraping_api = _UnconfiguredWebScrapingApi()  # type: ignore[assignment]
