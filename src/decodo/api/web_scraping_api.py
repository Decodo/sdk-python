from __future__ import annotations

from typing import cast

from decodo.generated.targets import ScrapeRequest
from decodo.http import HttpClient
from decodo.schema.types import DecodoSchema
from decodo.types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
)


class WebScrapingApi:
    def __init__(self, http: HttpClient, schema: DecodoSchema | None = None) -> None:
        self._http = http
        self._schema = schema

    def scrape(self, params: ScrapeRequest) -> SyncResponse:
        return cast(SyncResponse, self._http.post("/v2/scrape", params.model_dump(exclude_none=True, mode="json")))

    def scrape_async(self, params: ScrapeRequest) -> AsyncTaskResponse:
        return cast(AsyncTaskResponse, self._http.post("/v3/task", params.model_dump(exclude_none=True, mode="json")))

    def scrape_batch(self, params: ScrapeRequest) -> BatchResponse:
        return cast(BatchResponse, self._http.post("/v3/task/batch", params.model_dump(exclude_none=True, mode="json")))

    def get_status(self, task_id: str) -> TaskMetadata:
        return cast(TaskMetadata, self._http.get(f"/v3/task/{task_id}"))

    def get_results(self, task_id: str) -> TaskResultsResponse | None:
        result = self._http.get(f"/v3/task/{task_id}/results")
        return cast(TaskResultsResponse, result) if result is not None else None
