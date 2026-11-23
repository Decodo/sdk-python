from __future__ import annotations

import contextlib
import json
import os
import time
import warnings
from typing import Any, cast

import httpx

from .build_target_meta import build_target_meta
from .constants import DEFAULT_IR_BASE, DEFAULT_IR_CACHE_PATH, DEFAULT_IR_PREFIX
from .expand_path import expand_path
from .resolve_latest_ir import resolve_latest_ir
from .types import (
    CachedIr,
    DecodoSchema,
    IrEndpoint,
    RemoteIr,
    RemoteSchemaLoadOptions,
    TargetMeta,
    build_endpoint_request_schemas,
    ir_section,
)


def _read_cached_ir(cache_path: str) -> CachedIr | None:
    try:
        with open(cache_path, encoding="utf-8") as f:
            return cast(CachedIr, json.load(f))
    except Exception:
        return None


def _is_cache_fresh(cached: CachedIr, ttl_ms: int | None) -> bool:
    if ttl_ms is None:
        return True
    return (time.time() * 1000 - cached["fetched_at"]) < ttl_ms


def _fetch_ir(url: str) -> RemoteIr:
    response = httpx.get(url, headers={"Accept": "application/json"})
    if not response.is_success:
        raise RuntimeError(f"Failed to fetch IR from {url}: HTTP {response.status_code}")
    return cast(RemoteIr, response.json())


def _write_cached_ir(cache_path: str, cached: CachedIr) -> None:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cached, f, indent=2)


def _resolve_ir_url(
    options: RemoteSchemaLoadOptions,
) -> tuple[str, str | None]:
    url = options.get("url")
    if url:
        return url, None
    latest = resolve_latest_ir()
    return latest["url"], latest["version"]


def _load_ir(options: RemoteSchemaLoadOptions) -> RemoteIr:
    cache_path = expand_path(options.get("cache_path") or DEFAULT_IR_CACHE_PATH)
    cached = _read_cached_ir(cache_path)
    ttl_ms = options.get("ttl_ms")
    usable = cached if cached is not None and _is_cache_of(cached, options.get("url")) else None

    if usable is not None and ttl_ms is not None and _is_cache_fresh(usable, ttl_ms):
        return usable["ir"]

    try:
        return _refresh_ir(options, cache_path, cached)
    except (httpx.HTTPError, RuntimeError, ValueError) as error:
        if usable is None:
            raise
        warnings.warn(
            f"Could not refresh the Decodo IR ({type(error).__name__}); using the cached copy.",
            RuntimeWarning,
            stacklevel=3,
        )
        return usable["ir"]


def _is_cache_of(cached: CachedIr, url: str | None) -> bool:
    resolved_url = cached.get("resolved_url") or ""
    if url:
        return resolved_url == url
    return resolved_url.startswith(f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}")


def _refresh_ir(options: RemoteSchemaLoadOptions, cache_path: str, cached: CachedIr | None) -> RemoteIr:
    resolved_url, resolved_version = _resolve_ir_url(options)
    ttl_ms = options.get("ttl_ms")

    if cached is not None and cached.get("resolved_url") == resolved_url:
        if _is_cache_fresh(cached, ttl_ms):
            return cached["ir"]

        if options.get("url") or cached["ir"].get("version") == resolved_version:
            with contextlib.suppress(OSError):
                _write_cached_ir(cache_path, CachedIr(**{**cached, "fetched_at": int(time.time() * 1000)}))
            return cached["ir"]

    ir = _fetch_ir(resolved_url)
    _write_cached_ir(
        cache_path,
        CachedIr(
            fetched_at=int(time.time() * 1000),
            resolved_url=resolved_url,
            ir=ir,
        ),
    )
    return ir


def _build_parameter_schemas(ir: RemoteIr) -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for target_key, target in ir["apis"]["webScrapingApi"]["targets"].items():
        schemas[target_key] = target["parameter_schema"]
    return schemas


class RemoteSchema:
    def __init__(
        self,
        ir: RemoteIr,
        parameter_schemas: dict[str, dict[str, Any]],
    ) -> None:
        self._version = ir["version"]
        self._meta = build_target_meta(ir["apis"]["webScrapingApi"]["targets"])
        self._parameter_schemas = parameter_schemas
        self._request_schemas = {
            k: v["parameter_schema"]
            for k, v in ir["apis"]["webScrapingApi"]["targets"].items()
        }
        self._shared_parameters: dict[str, Any] = ir["apis"]["webScrapingApi"].get("parameters") or {}
        self._target_keys = list(ir["apis"]["webScrapingApi"]["targets"].keys())
        self._endpoint_schemas = build_endpoint_request_schemas(ir)
        self._operations = ir_section(ir, "operations")
        self._flows = ir_section(ir, "flows")
        self._surfaces = ir_section(ir, "surfaces")
        key_check = ir.get("keyCheck")
        self._key_check: dict[str, Any] | None = key_check if isinstance(key_check, dict) else None

    @classmethod
    def load(cls, options: RemoteSchemaLoadOptions | None = None) -> RemoteSchema:
        opts: RemoteSchemaLoadOptions = options or RemoteSchemaLoadOptions()
        ir = _load_ir(opts)
        parameter_schemas = _build_parameter_schemas(ir)
        return cls(ir, parameter_schemas)

    def get_request_schema(self, target: str) -> dict[str, Any] | None:
        return self._request_schemas.get(target)

    def list_targets(self) -> list[str]:
        return list(self._target_keys)

    def get_target_meta(self, target: str) -> TargetMeta | None:
        return self._meta.get(target)

    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None:
        return self._parameter_schemas.get(target)

    def get_shared_parameters(self) -> dict[str, Any]:
        return self._shared_parameters

    def get_endpoint_request_schema(self, endpoint: str) -> dict[str, Any] | None:
        return self._endpoint_schemas.get(endpoint)

    def get_flow(self, flow: str) -> dict[str, Any] | None:
        return self._flows.get(flow)

    def get_operation(self, operation: str) -> IrEndpoint | None:
        return cast(IrEndpoint | None, self._operations.get(operation))

    def get_key_check(self) -> dict[str, Any] | None:
        return self._key_check

    def get_surface(self, client: str) -> dict[str, Any] | None:
        return self._surfaces.get(client)

    @property
    def version(self) -> str | None:
        return self._version


# Satisfy DecodoSchema protocol
_: DecodoSchema = RemoteSchema.__new__(RemoteSchema)
