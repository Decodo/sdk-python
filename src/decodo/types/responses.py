from __future__ import annotations

from typing import Any, Literal, TypedDict


class ResultEntry(TypedDict, total=False):
    content: Any
    status_code: int
    url: str
    task_id: str
    headers: dict[str, str]
    cookies: list[dict[str, str]]
    created_at: str
    updated_at: str
    help: str
    browser_actions_warnings: list[dict[str, str]]
    browser_actions_error: list[dict[str, str]]
    delivery_zip: str


class SyncResponse(TypedDict):
    results: list[ResultEntry]


class AsyncTaskResponse(TypedDict, total=False):
    id: str
    target: str
    url: str
    query: str
    status: str
    created_at: str
    updated_at: str
    page_from: int
    limit: int
    geo: str | None
    device_type: str
    headless: str | None
    parse: bool
    locale: str | None
    domain: str
    output_schema: str | None
    content_encoding: str
    page_count: int
    adults: int
    children: int
    callback_url: str
    browser_actions_error: list[dict[str, str]]
    browser_actions_warnings: list[dict[str, str]]


class BatchResponse(TypedDict, total=False):
    id: str
    queries: list[AsyncTaskResponse]
    errors: list[dict[str, str]]


TaskStatus = Literal["pending", "faulted", "done"]


class TaskMetadata(TypedDict, total=False):
    status: TaskStatus


class TaskResultsResponse(TypedDict):
    results: list[ResultEntry]


class ErrorResponse(TypedDict, total=False):
    status: str
    message: str
    errors: list[Any]
