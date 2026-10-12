from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlsplit

import jsonschema
from pydantic import BaseModel

import decodo.errors
from decodo.http import HttpClient

if TYPE_CHECKING:
    from decodo.generated.targets import BatchRequest, ScrapeRequest
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.types import DecodoSchema
from decodo.types.data_api import (
    CrawlPage,
    CrawlPagesResponse,
    CrawlRequest,
    CrawlResponse,
    CrawlStatus,
    CrawlStatusResponse,
    MapRequest,
    MapResponse,
    SearchRequest,
    SearchResponse,
)
from decodo.types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
)


@dataclass(frozen=True)
class WebScrapingApiRoutes:
    scrape: str
    task: str
    search: str | None = None
    map: str | None = None
    crawl: str | None = None


SCRAPER_API_ROUTES = WebScrapingApiRoutes(scrape="/v2/scrape", task="/v3/task")
DATA_API_ROUTES = WebScrapingApiRoutes(
    scrape="/v1/scrape",
    task="/v1/task",
    search="/v1/search",
    map="/v1/map",
    crawl="/v1/crawl",
)


DEFAULT_CRAWL_POLL_INTERVAL = 5.0
_CRAWL_TERMINAL: frozenset[CrawlStatus] = frozenset({"done", "truncated", "faulted", "cancelled"})
_CRAWL_FAILED: frozenset[CrawlStatus] = frozenset({"faulted", "cancelled"})


def _to_payload(params: ScrapeRequest | BatchRequest | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(params, BaseModel):
        return params.model_dump(by_alias=True, exclude_none=True, mode="json")
    return dict(params)


class WebScrapingApi:
    def __init__(
        self,
        http: HttpClient,
        schema: DecodoSchema = BundledSchema.shared,
        routes: WebScrapingApiRoutes = SCRAPER_API_ROUTES,
    ) -> None:
        self._http = http
        self._schema = schema
        self._routes = routes

    def _validate(self, payload: dict[str, Any]) -> None:
        if self._schema is None:
            return
        if "target" not in payload:
            raise decodo.errors.ValidationError("missing required field 'target'")
        schema = self._schema.get_request_schema(payload.get("target"))  # type: ignore[arg-type]
        if not schema:
            target = payload["target"]
            valid = self._schema.list_targets()
            if target not in valid:
                raise decodo.errors.ValidationError(
                    f"unknown target {target!r}. Valid targets: {', '.join(sorted(valid))}"
                )
            return
        try:
            jsonschema.validate(payload, schema)
        except jsonschema.ValidationError as e:
            raise decodo.errors.ValidationError(str(e)) from e

    def scrape(self, params: ScrapeRequest | Mapping[str, Any]) -> SyncResponse:
        payload = _to_payload(params)
        self._validate(payload)
        return cast(SyncResponse, self._http.post(self._routes.scrape, payload))

    def scrape_async(self, params: ScrapeRequest | Mapping[str, Any]) -> AsyncTaskResponse:
        payload = _to_payload(params)
        self._validate(payload)
        return cast(AsyncTaskResponse, self._http.post(self._routes.task, payload))

    def scrape_batch(self, params: BatchRequest | Mapping[str, Any]) -> BatchResponse:
        payload = _to_payload(params)
        return cast(BatchResponse, self._http.post(f"{self._routes.task}/batch", payload))

    def get_status(self, task_id: str) -> TaskMetadata:
        return cast(TaskMetadata, self._http.get(f"{self._routes.task}/{task_id}"))

    def get_results(self, task_id: str) -> TaskResultsResponse | None:
        result = self._http.get(f"{self._routes.task}/{task_id}/results")
        return cast(TaskResultsResponse, result) if result is not None else None

    def _data_api_route(self, route: str, method: str) -> str:
        path: str | None = getattr(self._routes, route)
        if path is None:
            raise ValueError(
                f"{method} requires an API key. "
                "Configure web_scraping_api with api_key instead of token."
            )
        return path

    def _validate_endpoint(self, endpoint: str, payload: dict[str, Any]) -> None:
        if self._schema is None:
            return
        schema = self._schema.get_endpoint_request_schema(endpoint)
        if not schema:
            return
        try:
            jsonschema.validate(payload, schema)
        except jsonschema.ValidationError as e:
            raise decodo.errors.ValidationError(str(e)) from e

    def search(self, params: SearchRequest | Mapping[str, Any]) -> SearchResponse:
        path = self._data_api_route("search", "search")
        payload = dict(params)
        self._validate_endpoint("runSearch", payload)
        return cast(SearchResponse, self._http.post(path, payload))

    def map(self, params: MapRequest | Mapping[str, Any]) -> MapResponse:
        path = self._data_api_route("map", "map")
        payload = dict(params)
        self._validate_endpoint("mapSite", payload)
        return cast(MapResponse, self._http.post(path, payload))

    def start_crawl(self, params: CrawlRequest | Mapping[str, Any]) -> CrawlResponse:
        path = self._data_api_route("crawl", "start_crawl")
        payload = dict(params)
        self._validate_endpoint("startCrawl", payload)
        return cast(CrawlResponse, self._http.post(path, payload))

    def get_crawl_status(self, crawl_id: str) -> CrawlStatusResponse:
        path = self._data_api_route("crawl", "get_crawl_status")
        return cast(CrawlStatusResponse, self._http.get(f"{path}/{crawl_id}/status"))

    def cancel_crawl(self, crawl_id: str) -> CrawlResponse:
        path = self._data_api_route("crawl", "cancel_crawl")
        return cast(CrawlResponse, self._http.post(f"{path}/{crawl_id}/cancel", None))

    def get_crawl_results(self, crawl_id: str, *, content: bool = True) -> list[CrawlPage]:
        """Return every page of a crawl, following ``next`` until the last page.

        With ``content=True`` (the default) each page carries its body; the API
        serves those in smaller pages, so this makes more requests.
        """
        path = self._data_api_route("crawl", "get_crawl_results")
        query = {"type": "content"} if content else None
        body = cast(CrawlPagesResponse, self._http.get(f"{path}/{crawl_id}", query))

        pages: list[CrawlPage] = list(body.get("url") or [])
        while next_url := body.get("next"):
            parts = urlsplit(next_url)
            next_path = f"{parts.path}?{parts.query}" if parts.query else parts.path
            body = cast(CrawlPagesResponse, self._http.get(next_path))
            pages.extend(body.get("url") or [])
        return pages

    def crawl(
        self,
        params: CrawlRequest | Mapping[str, Any],
        *,
        poll_interval: float = DEFAULT_CRAWL_POLL_INTERVAL,
        timeout: float | None = None,
    ) -> list[CrawlPage]:
        """Start a crawl, wait for it to finish, and return every page with its content.

        Polls ``get_crawl_status`` every ``poll_interval`` seconds. ``timeout`` is the
        maximum number of seconds to wait; ``None`` waits until the server settles the
        crawl, which it does after the request's ``max_duration``. On timeout raises
        ``CrawlTimeoutError`` carrying the ``crawl_id``; the crawl keeps running.
        Raises ``CrawlError`` if the crawl ends ``faulted`` or ``cancelled``, and
        ``CrawlInterruptedError`` (also carrying ``crawl_id``) if a status or results
        request fails after the crawl was started.
        """
        if poll_interval <= 0:
            raise ValueError("poll_interval must be a positive number of seconds.")
        self._data_api_route("crawl", "crawl")

        crawl_id = self.start_crawl(params)["crawl_id"]
        started = time.monotonic()

        try:
            while True:
                status = self.get_crawl_status(crawl_id)
                state = status.get("status")
                if state in _CRAWL_TERMINAL:
                    break
                if timeout is None:
                    time.sleep(poll_interval)
                    continue
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise decodo.errors.CrawlTimeoutError(crawl_id, timeout)
                time.sleep(min(poll_interval, remaining))

            if state in _CRAWL_FAILED:
                raise decodo.errors.CrawlError(crawl_id, cast(str, state), status.get("reason"))
            return self.get_crawl_results(crawl_id)
        except (decodo.errors.DecodoError, decodo.errors.TimeoutError) as err:
            if isinstance(err, (decodo.errors.CrawlError, decodo.errors.CrawlTimeoutError)):
                raise
            raise decodo.errors.CrawlInterruptedError(crawl_id, err) from err
