"""Request and response types for the Data API endpoints: search, map and crawl.

Transcribed from the ``dataApi`` section of the Decodo IR (v2.3.0).
Timestamps are UTC strings formatted as ``YYYY-MM-DD HH:MM:SS``, not RFC 3339.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

# --- search -----------------------------------------------------------------


class SearchRequest(TypedDict, total=False):
    query: str
    url: str
    uule: str
    gl: str
    geo: str
    locale: str
    input_encoding: str
    page: int


class SearchOrganicResult(TypedDict, total=False):
    link: str
    original_link: str
    title: str
    description: str
    extensions: list[Any]
    rank: int


class SearchTopStory(TypedDict, total=False):
    title: str
    link: str
    site: str
    ago: str
    rank: int


class SearchPeopleAlsoAsk(TypedDict, total=False):
    question: str
    link: str


class SearchRelatedSearch(TypedDict, total=False):
    query: str
    link: str


class SearchParameters(TypedDict, total=False):
    engine: str
    query: str
    locale: str
    gl: str


class SearchResponse(TypedDict, total=False):
    """The upstream search document.

    On a scrape failure the API still answers 200 with ``status: "failed"``,
    a ``message`` and optionally ``status_code`` and ``task_id``.
    """

    status: str
    url: str
    organic: list[SearchOrganicResult]
    top_stories: list[SearchTopStory]
    people_also_ask: list[SearchPeopleAlsoAsk]
    related_searches: list[SearchRelatedSearch]
    answer_box: dict[str, Any]
    search_parameters: SearchParameters
    status_code: int
    message: str
    task_id: str


# --- map --------------------------------------------------------------------

SitemapMode = Literal["include", "only", "skip"]
DomainFilter = Literal["domain", "subdomain", "all"]
PathPatterns = str | list[str]


class MapRequest(TypedDict, total=False):
    url: str
    limit: int
    sitemap: SitemapMode
    domain_filter: DomainFilter
    geo: str
    locale: str
    JS_rendering: bool
    follow_redirects: bool
    select_paths: PathPatterns
    exclude_paths: PathPatterns


class MapLink(TypedDict):
    url: str


class MapContent(TypedDict):
    links: list[MapLink]


class MapResult(TypedDict):
    content: MapContent
    status_code: int
    url: str
    sitemap_status: SitemapMode
    map_id: str
    created_at: str
    updated_at: str


class MapResponse(TypedDict):
    results: list[MapResult]


# --- crawl ------------------------------------------------------------------

CrawlOutput = Literal["markdown", "html"]
CrawlStatus = Literal["pending", "done", "faulted", "cancelled", "truncated"]
CrawlStopReason = Literal["max_duration", "vendor_limit", "no_pages_found"]
CrawlPageStatus = Literal["pending", "done", "faulted"]


class CrawlRequest(TypedDict, total=False):
    url: str
    limit: int
    max_depth: int
    sitemap: SitemapMode
    domain_filter: DomainFilter
    output: CrawlOutput
    geo: str
    locale: str
    follow_redirects: bool
    JS_retry: bool
    max_duration: int
    callback_url: str
    passthrough: str
    select_paths: PathPatterns
    exclude_paths: PathPatterns


class CrawlResponse(TypedDict):
    """Returned by ``start_crawl`` and ``cancel_crawl``."""

    target: Literal["crawl"]
    url: str
    created_at: str
    crawl_id: str
    status: CrawlStatus
    crawl_status: str
    results_tasks: str
    results_content: str


class CrawlStatusResponse(TypedDict, total=False):
    target: Literal["crawl"]
    url: str
    created_at: str
    crawl_id: str
    status: CrawlStatus
    reason: CrawlStopReason
    sitemap_status: SitemapMode
    output: CrawlOutput
    discovered: int
    completed: int
    failed: int
    in_flight: int
    sitemaps: int
    requests: int


class CrawlPage(TypedDict, total=False):
    task_id: str
    status: CrawlPageStatus
    created_at: str
    updated_at: str
    url: str
    depth: int
    parent_url: str
    result_key: str
    content: str
    content_error: str
    crawl_status: str
    results_tasks: str
    results_content: str


class CrawlPagesResponse(TypedDict, total=False):
    """One page of ``GET /v1/crawl/{id}``. The pages are under ``url``, not ``results``."""

    crawl_id: str
    url: list[CrawlPage]
    next: str
    total: int
