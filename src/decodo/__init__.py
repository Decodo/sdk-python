from .api.web_scraping_api import WebScrapingApi, WebScrapingApiRoutes
from .client import DecodoClient, DecodoConfig, WebScrapingApiConfig
from .errors import (
    AuthenticationError,
    CrawlError,
    CrawlInterruptedError,
    CrawlTimeoutError,
    DecodoError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .schema.bundled_schema import BundledSchema
from .schema.remote_schema import RemoteSchema
from .schema.types import DecodoSchema, RemoteSchemaLoadOptions
from .targets import Target, targets
from .types.data_api import (
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
from .types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    ResultEntry,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
    TaskStatus,
)

_GENERATED_PARAMETER_NAMES = ("ParameterMeta", "parameter_meta")

_codegen_available = False
_CODEGEN_NAMES: frozenset[str] = frozenset()
try:
    from .generated import targets as _generated_targets
    from .generated.parameters import ParameterMeta, parameter_meta  # noqa: F401

    # Read before the star import: generated files from before __all__ was emitted
    # fall through to the "run codegen" hint instead of re-exporting their imports.
    _CODEGEN_NAMES = frozenset([*_GENERATED_PARAMETER_NAMES, *_generated_targets.__all__])
    from .generated.targets import *  # noqa: F403

    _codegen_available = True
except (ImportError, AttributeError):
    _CODEGEN_NAMES = frozenset()


def _is_codegen_name(name: str) -> bool:
    return name.endswith("Params") or name in {
        *_GENERATED_PARAMETER_NAMES,
        "ScrapeRequest",
        "BatchRequest",
        "target_meta",
    }


def __getattr__(name: str) -> object:
    if not _codegen_available and _is_codegen_name(name):
        raise ImportError(
            f"'{name}' requires generated types. "
            "Editable install: run python -m decodo.codegen.codegen, then use 'from decodo import ...'. "
            "Pip install: run python -m decodo.codegen.codegen --out-dir ./decodo_generated, "
            "then use 'from decodo_generated.targets import ...'."
        )
    raise AttributeError(f"module 'decodo' has no attribute {name!r}")


__all__ = [
    "DecodoClient",
    "DecodoConfig",
    "WebScrapingApiConfig",
    "WebScrapingApi",
    "WebScrapingApiRoutes",
    "BundledSchema",
    "RemoteSchema",
    "DecodoSchema",
    "RemoteSchemaLoadOptions",
    "Target",
    "targets",
    "SyncResponse",
    "AsyncTaskResponse",
    "BatchResponse",
    "TaskMetadata",
    "TaskResultsResponse",
    "TaskStatus",
    "ResultEntry",
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
    "DecodoError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
    "CrawlError",
    "CrawlInterruptedError",
    "CrawlTimeoutError",
]

__all__ += sorted(_CODEGEN_NAMES)
