from __future__ import annotations

from decodo.errors import ValidationError
from decodo.http import HttpClient
from decodo.generated.targets import ScrapeRequest
from decodo.types.responses import (
    AsyncTaskResponse,
    BatchResponse,
    SyncResponse,
    TaskMetadata,
    TaskResultsResponse,
)


class WebScrapingApi:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def scrape(self, params: ScrapeRequest) -> SyncResponse:
        return self._http.post("/v2/scrape", params.model_dump(exclude_none=True, mode="json"))

    def scrape_async(self, params: ScrapeRequest) -> AsyncTaskResponse:
        return self._http.post("/v3/task", params.model_dump(exclude_none=True, mode="json"))

    def scrape_batch(self, params: ScrapeRequest) -> BatchResponse:
        return self._http.post("/v3/task/batch", params.model_dump(exclude_none=True, mode="json"))

    def get_status(self, task_id: str) -> TaskMetadata:
        return self._http.get(f"/v3/task/{task_id}")

    def get_results(self, task_id: str) -> TaskResultsResponse | None:
        result = self._http.get(f"/v3/task/{task_id}/results")
        return result if result is not None else None
