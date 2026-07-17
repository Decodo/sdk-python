from __future__ import annotations

from typing import Any, Protocol, TypedDict


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


class RemoteIrApis(TypedDict):
    webScrapingApi: WebScrapingApiIr


class WebScrapingApiIr(TypedDict):
    parameters: dict[str, Any]
    targets: dict[str, IrTarget]


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

    @property
    def version(self) -> str | None: ...
