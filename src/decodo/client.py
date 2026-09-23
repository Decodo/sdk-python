from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .api.web_scraping_api import (
    DATA_API_ROUTES,
    SCRAPER_API_ROUTES,
    WebScrapingApi,
    WebScrapingApiRoutes,
)
from .http import ApiKeyAuth, BasicAuth, HttpClient, HttpClientConfig
from .schema.bundled_schema import BundledSchema
from .schema.types import DecodoSchema

WEB_API_BASE_URL = "https://scraper-api.decodo.com"
DATA_API_BASE_URL = "https://data.decodo.com"
DEFAULT_TIMEOUT_MS = 180_000


@dataclass
class WebScrapingApiConfig:
    token: str | None = None
    api_key: str | None = None
    integration_header: str | None = None


@dataclass
class DecodoConfig:
    web_scraping_api: WebScrapingApiConfig | None = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    schema: DecodoSchema | None = None


@dataclass(frozen=True)
class _Transport:
    base_url: str
    auth: BasicAuth | ApiKeyAuth
    routes: WebScrapingApiRoutes


def _present(value: str | None) -> str | None:
    return value if value is not None and value.strip() else None


def _resolve_transport(config: WebScrapingApiConfig) -> _Transport:
    token = _present(config.token)
    api_key = _present(config.api_key)

    if token is not None and api_key is not None:
        raise ValueError(
            "web_scraping_api accepts either token or api_key, not both. Provide only one."
        )

    if api_key is not None:
        return _Transport(
            base_url=DATA_API_BASE_URL,
            auth=ApiKeyAuth(type="apiKey", api_key=api_key),
            routes=DATA_API_ROUTES,
        )

    if token is not None:
        return _Transport(
            base_url=WEB_API_BASE_URL,
            auth=BasicAuth(type="basic", token=token),
            routes=SCRAPER_API_ROUTES,
        )

    raise ValueError("web_scraping_api requires token in DecodoConfig.")


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
            transport = _resolve_transport(config.web_scraping_api)
            http = HttpClient(
                HttpClientConfig(
                    base_url=transport.base_url,
                    auth=transport.auth,
                    timeout_ms=timeout_ms,
                    integration_header=config.web_scraping_api.integration_header,
                )
            )
            self.web_scraping_api = WebScrapingApi(http, schema, transport.routes)
        else:
            self.web_scraping_api = _UnconfiguredWebScrapingApi()  # type: ignore[assignment]
