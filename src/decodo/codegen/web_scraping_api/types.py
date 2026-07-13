from __future__ import annotations

from typing import Any, TypedDict


class IRTarget(TypedDict):
    group: str
    response_format: str
    parameter_schema: dict[str, Any]


class WebScrapingApiIR(TypedDict):
    label: str
    baseUrl: str
    auth: dict[str, Any]
    endpoints: dict[str, dict[str, str]]
    targets: dict[str, IRTarget]


class IR(TypedDict):
    version: str
    apis: IRApis


class IRApis(TypedDict):
    webScrapingApi: WebScrapingApiIR
