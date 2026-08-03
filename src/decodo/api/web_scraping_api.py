from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast

import jsonschema
from pydantic import BaseModel

import decodo.errors
from decodo.http import HttpClient

if TYPE_CHECKING:
    from decodo.generated.targets import BatchRequest, ScrapeRequest
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.types import DecodoSchema
from decodo.types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
)


def _to_payload(params: ScrapeRequest | BatchRequest | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(params, BaseModel):
        return params.model_dump(by_alias=True, exclude_none=True, mode="json")
    return dict(params)


class WebScrapingApi:
    def __init__(self, http: HttpClient, schema: DecodoSchema = BundledSchema.shared) -> None:
        self._http = http
        self._schema = schema

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
        return cast(SyncResponse, self._http.post("/v2/scrape", payload))

    def scrape_async(self, params: ScrapeRequest | Mapping[str, Any]) -> AsyncTaskResponse:
        payload = _to_payload(params)
        self._validate(payload)
        return cast(AsyncTaskResponse, self._http.post("/v3/task", payload))

    def scrape_batch(self, params: BatchRequest | Mapping[str, Any]) -> BatchResponse:
        payload = _to_payload(params)
        return cast(BatchResponse, self._http.post("/v3/task/batch", payload))

    def get_status(self, task_id: str) -> TaskMetadata:
        return cast(TaskMetadata, self._http.get(f"/v3/task/{task_id}"))

    def get_results(self, task_id: str) -> TaskResultsResponse | None:
        result = self._http.get(f"/v3/task/{task_id}/results")
        return cast(TaskResultsResponse, result) if result is not None else None
