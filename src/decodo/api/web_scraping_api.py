from __future__ import annotations

from typing import Any

import jsonschema

from decodo.errors import ValidationError
from decodo.http import HttpClient
from decodo.schema.bundled_schema import BundledSchema
from decodo.schema.types import DecodoSchema
from decodo.types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
)


class WebScrapingApi:
    def __init__(
        self,
        http: HttpClient,
        schemas: DecodoSchema | None = None,
    ) -> None:
        self._http = http
        self._schemas: DecodoSchema = schemas if schemas is not None else BundledSchema.shared

    def _validate(self, params: dict[str, Any]) -> None:
        target = params.get("target", "")
        schema = self._schemas.get_request_schema(str(target))
        if schema is None:
            return
        validator = jsonschema.Draft4Validator(schema)
        errors = list(validator.iter_errors(params))
        if errors:
            messages = "; ".join(e.message for e in errors)
            raise ValidationError(messages, [e.message for e in errors])

    def scrape(self, params: dict[str, Any]) -> SyncResponse:
        self._validate(params)
        return self._http.post("/v2/scrape", params)

    def scrape_async(self, params: dict[str, Any]) -> AsyncTaskResponse:
        self._validate(params)
        return self._http.post("/v3/task", params)

    def scrape_batch(self, params: dict[str, Any]) -> BatchResponse:
        return self._http.post("/v3/task/batch", params)

    def get_status(self, task_id: str) -> TaskMetadata:
        return self._http.get(f"/v3/task/{task_id}")

    def get_results(self, task_id: str) -> TaskResultsResponse | None:
        result = self._http.get(f"/v3/task/{task_id}/results")
        return result if result is not None else None
