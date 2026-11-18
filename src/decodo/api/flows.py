"""Runs the flows the Decodo IR describes: a single call, a job, or a batch of jobs.

Which endpoints a flow uses, where its job id and status are, and which statuses
mean "still running" all come from the IR, so a flow added there needs no new code
here.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any, cast
from urllib.parse import quote, urlencode, urlsplit

import jsonschema

import decodo.errors
from decodo.http import HttpClient
from decodo.schema.types import DecodoSchema, FlowSchema

DEFAULT_POLL_INTERVAL = 5.0

Flow = dict[str, Any]


def _local_path(path: Any) -> str:
    """A path on the configured host. Anything that could name another host is refused,
    because the API key is sent with the request."""
    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//") or "\\" in path:
        raise ValueError("The schema gave a request path that is not a path on the API host.")
    return path


class Flows:
    def __init__(self, http: HttpClient, schema: DecodoSchema, *, available: bool) -> None:
        self._http = http
        self._schema = schema
        self._available = available

    def describe(self, flow: str, pattern: str | None = None) -> Flow:
        """The IR's description of a flow. Raises ``ValueError`` if it is unknown or of another pattern."""
        if not self._available:
            raise ValueError("Flows require an API key. Configure web_scraping_api with api_key instead of token.")
        if not isinstance(self._schema, FlowSchema):
            raise ValueError("The schema in use has no flows; they need Decodo IR 2.6.0 or newer.")
        found = self._schema.get_flow(flow)
        if found is None:
            raise ValueError(f"Unknown flow {flow!r}.")
        if pattern is not None and found.get("pattern") != pattern:
            raise ValueError(f"Flow {flow!r} is a {found.get('pattern')} flow, not a {pattern} flow.")
        return found

    def check_key(self) -> None:
        """Send the request the IR gives for checking an API key.

        Returns when Decodo accepted the key. Raises ``AuthenticationError`` when it rejected
        the key, and ``RateLimitError``, ``TimeoutError`` or a transport error when the check
        proved nothing. The request scrapes a host that never resolves, so it costs nothing.
        """
        self.describe("scrape")
        check = cast(FlowSchema, self._schema).get_key_check()
        if not check or not isinstance(check.get("params"), Mapping):
            raise ValueError("The schema in use has no key check; it needs Decodo IR 2.6.0 or newer.")
        try:
            self.call(check["flow"], check["params"])
        except (decodo.errors.AuthenticationError, decodo.errors.RateLimitError):
            raise
        except decodo.errors.DecodoError:
            # Any other answer means the key was read and accepted before the target failed.
            return

    def call(self, flow: str, params: Mapping[str, Any]) -> Any:
        """Run a ``call`` flow: one request, and its response."""
        return self._send(self.describe(flow, "call")["run"], body=dict(params))

    def start(self, flow: str, params: Mapping[str, Any]) -> dict[str, Any]:
        """Start a ``job`` flow. The response holds the job id under the flow's ``idField``."""
        return cast(dict[str, Any], self._send(self.describe(flow, "job")["start"], body=dict(params)))

    def start_batch(self, flow: str, params: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Run a ``batch`` flow and return the jobs it started, each a start response of the flow's job."""
        described = self.describe(flow, "batch")
        response = self._send(described["start"], body=dict(params))
        return list(response.get(described["itemsField"]) or [])

    def status(self, flow: str, job_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], self._send(self.describe(flow, "job")["status"], job_id=job_id))

    def is_pending(self, flow: str, status: Mapping[str, Any]) -> bool:
        described = self.describe(flow, "job")
        return status.get(described["statusField"]) in described["pendingStatuses"]

    def has_failed(self, flow: str, status: Mapping[str, Any]) -> bool:
        described = self.describe(flow, "job")
        return status.get(described["statusField"]) in described["failedStatuses"]

    def wait(
        self,
        flow: str,
        job_id: str,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Poll a job until it is no longer pending and return its final status, failed or not.

        ``poll_interval`` defaults to the interval the IR gives the flow. ``timeout`` is the
        maximum number of seconds to wait. On timeout raises ``JobTimeoutError`` carrying the
        flow and job id; the job keeps running.
        """
        if poll_interval is None:
            poll_interval = self._poll_seconds(flow)
        if poll_interval <= 0:
            raise ValueError("poll_interval must be a positive number of seconds.")
        started = time.monotonic()

        while True:
            status = self.status(flow, job_id)
            if not self.is_pending(flow, status):
                return status
            if timeout is None:
                time.sleep(poll_interval)
                continue
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise decodo.errors.JobTimeoutError(flow, job_id, timeout)
            time.sleep(min(poll_interval, remaining))

    def _poll_seconds(self, flow: str) -> float:
        published = self.describe(flow, "job").get("pollSeconds")
        if isinstance(published, (int, float)) and not isinstance(published, bool) and published > 0:
            return float(published)
        return DEFAULT_POLL_INTERVAL

    def results(self, flow: str, job_id: str, *, max_items: int | None = None) -> Any:
        """A job's results: its items when the flow pages them, otherwise the response as it is.

        Every page is read unless ``max_items`` is given; then reading stops at the page
        that reaches it, so the list can run a little over.
        """
        described = self.describe(flow, "job")
        body = self._send(described["results"], job_id=job_id, query=described.get("resultsQuery"))
        pagination = described.get("pagination")
        if not pagination:
            return body

        items: list[Any] = list((body or {}).get(pagination["itemsField"]) or [])
        while (next_url := (body or {}).get(pagination["nextField"])) and (max_items is None or len(items) < max_items):
            parts = urlsplit(next_url)
            path = _local_path(parts.path)
            body = self._http.get(f"{path}?{parts.query}" if parts.query else path)
            items.extend((body or {}).get(pagination["itemsField"]) or [])
        return items

    def cancel(self, flow: str, job_id: str) -> dict[str, Any]:
        endpoint = self.describe(flow, "job").get("cancel")
        if not endpoint:
            raise ValueError(f"Flow {flow!r} cannot be cancelled.")
        return cast(dict[str, Any], self._send(endpoint, job_id=job_id))

    def _send(
        self,
        endpoint: str,
        *,
        body: dict[str, Any] | None = None,
        job_id: str | None = None,
        query: Mapping[str, str] | None = None,
    ) -> Any:
        described = cast(FlowSchema, self._schema).get_operation(endpoint)
        if described is None:
            raise ValueError(f"The schema has no operation {endpoint!r}.")
        path = _local_path(described["path"])
        if job_id is not None:
            before, _, rest = path.partition("{")
            _, closed, after = rest.partition("}")
            if not closed or not str(job_id):
                raise ValueError(f"Operation {endpoint!r} needs a job id and a path with a place for it.")
            # Quoted whole, so an id can never add a path segment or a query and reach another endpoint.
            path = before + quote(str(job_id), safe="") + after
        if query:
            path = f"{path}?{urlencode(query)}"
        if body is not None:
            self._validate(described, body)
        return self._http.request(described["method"], path, body)

    def _validate(self, endpoint: Mapping[str, Any], body: dict[str, Any]) -> None:
        schema = endpoint.get("requestSchema")
        target = body.get("target")
        if not (schema and "properties" in schema) and isinstance(target, str):
            # Scrape and task bodies differ per target, so the endpoint lists no fields of its own.
            schema = self._schema.get_request_schema(target) or schema
        if not schema:
            return
        try:
            jsonschema.validate(body, schema)
        except jsonschema.ValidationError as e:
            raise decodo.errors.ValidationError(str(e)) from e
