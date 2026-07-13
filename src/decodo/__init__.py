from .client import DecodoClient, DecodoConfig, WebScrapingApiConfig
from .api.web_scraping_api import WebScrapingApi
from .schema.bundled_schema import BundledSchema
from .schema.remote_schema import RemoteSchema
from .schema.types import DecodoSchema, RemoteSchemaLoadOptions
from .generated.targets import Target, target_meta, targets
from .generated.parameters import ParameterMeta, parameter_meta
from .types.responses import (
    SyncResponse,
    AsyncTaskResponse,
    BatchResponse,
    TaskMetadata,
    TaskResultsResponse,
    TaskStatus,
    ResultEntry,
)
from .errors import (
    DecodoError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    TimeoutError,
)

__all__ = [
    "DecodoClient",
    "DecodoConfig",
    "WebScrapingApiConfig",
    "WebScrapingApi",
    "BundledSchema",
    "RemoteSchema",
    "DecodoSchema",
    "RemoteSchemaLoadOptions",
    "Target",
    "target_meta",
    "targets",
    "ParameterMeta",
    "parameter_meta",
    "SyncResponse",
    "AsyncTaskResponse",
    "BatchResponse",
    "TaskMetadata",
    "TaskResultsResponse",
    "TaskStatus",
    "ResultEntry",
    "DecodoError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
]
