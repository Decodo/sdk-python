from __future__ import annotations

from typing import Any, Protocol, Required, TypedDict


class TargetMeta(TypedDict):
    group: str
    response_format: str
    parameters: list[str]


class IrTarget(TypedDict):
    group: str
    response_format: str
    parameter_schema: dict[str, Any]


class RemoteIr(TypedDict):
    version: str
    apis: RemoteIrApis


class RemoteIrApis(TypedDict, total=False):
    webScrapingApi: Required[WebScrapingApiIr]
    dataApi: DataApiIr


class WebScrapingApiIr(TypedDict):
    parameters: dict[str, Any]
    targets: dict[str, IrTarget]


class IrEndpoint(TypedDict, total=False):
    method: str
    path: str
    requestSchema: dict[str, Any]
    responseSchema: dict[str, Any]


class DataApiIr(TypedDict):
    endpoints: dict[str, IrEndpoint]


class CachedIr(TypedDict):
    fetched_at: int
    resolved_url: str
    ir: RemoteIr


class GcsObjectListItem(TypedDict):
    name: str


class GcsObjectList(TypedDict, total=False):
    items: list[GcsObjectListItem]


class LatestIrLocation(TypedDict):
    version: str
    url: str


class RemoteSchemaLoadOptions(TypedDict, total=False):
    url: str
    cache_path: str
    ttl_ms: int


class DecodoSchema(Protocol):
    def get_request_schema(self, target: str) -> dict[str, Any] | None: ...
    def list_targets(self) -> list[str]: ...
    def get_target_meta(self, target: str) -> TargetMeta | None: ...
    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None: ...
    def get_shared_parameters(self) -> dict[str, Any]: ...
    def get_endpoint_request_schema(self, endpoint: str) -> dict[str, Any] | None:
        """Request schema of a Data API endpoint (``runSearch``, ``mapSite``, ``startCrawl``...)."""
        ...

    @property
    def version(self) -> str | None: ...


def build_endpoint_request_schemas(ir: RemoteIr) -> dict[str, dict[str, Any]]:
    """Collect the request schemas of the IR's Data API endpoints, if the section exists."""
    data_api = ir["apis"].get("dataApi")
    if data_api is None:
        return {}
    return {
        name: endpoint["requestSchema"]
        for name, endpoint in data_api.get("endpoints", {}).items()
        if "requestSchema" in endpoint
    }
