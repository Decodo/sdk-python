from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from decodo.errors import ResultError

_MISSING: Any = object()
_RETRYABLE_STATUS = 429
_SERVER_ERROR = 500


def _at(value: Any, path: str) -> Any:
    segment, _, rest = path.partition(".")
    if segment == "*":
        if not isinstance(value, list):
            return _MISSING
        found = [_at(item, rest) if rest else item for item in value]
        return [item for item in found if item is not _MISSING]
    if segment.isdigit():
        index = int(segment)
        step = value[index] if isinstance(value, list) and index < len(value) else _MISSING
    else:
        step = value.get(segment, _MISSING) if isinstance(value, Mapping) else _MISSING
    return _at(step, rest) if rest and step is not _MISSING else step


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _raise_if_failed(failure: Mapping[str, Any], response: Any) -> None:
    value = _at(response, failure["path"])
    if "equals" in failure:
        failed = value is not _MISSING and value == failure["equals"]
    else:
        failed = _is_number(value) and value >= failure["atLeast"]
    if not failed:
        return

    code = _at(response, failure["code"]) if failure.get("code") else _MISSING
    code = value if code is _MISSING or code is None else code
    message = _at(response, failure["message"]) if failure.get("message") else _MISSING
    retryable = bool(failure.get("retryable")) or (
        _is_number(code) and (code == _RETRYABLE_STATUS or code >= _SERVER_ERROR)
    )
    text = message if isinstance(message, str) and message else f"Decodo reported a failure ({code})."
    raise ResultError(text, str(code), retryable=retryable)


def _picked(item: Any, rule: Mapping[str, Any]) -> Any:
    fields = rule.get("fields")
    if fields:
        picked = {name: None if (value := _at(item, path)) is _MISSING else value for name, path in fields.items()}
        for name in rule.get("required") or ():
            if picked.get(name) in (None, "", [], {}):
                raise ResultError(f"Decodo returned a result with no {name}.", f"empty_{name}")
        return picked
    omit = rule.get("omit")
    if omit and isinstance(item, Mapping):
        return {name: value for name, value in item.items() if name not in omit}
    return item


def read_result(rule: Mapping[str, Any] | None, response: Any) -> Any:
    if not rule:
        return response
    for failure in rule.get("failures") or ():
        _raise_if_failed(failure, response)

    result = _at(response, rule["from"]) if rule.get("from") else response
    if result is _MISSING or result is None:
        raise ResultError("Decodo returned no result.", "empty_response")
    if isinstance(result, list):
        return [_picked(item, rule) for item in result]
    return _picked(result, rule)


def check_result_rule(rule: Any) -> None:
    if not isinstance(rule, Mapping):
        raise TypeError("the result rule is not an object")
    failures = rule.get("failures") or []
    if not isinstance(failures, list):
        raise TypeError("failures is not a list")
    for failure in failures:
        if not isinstance(failure, Mapping) or not isinstance(failure.get("path"), str):
            raise TypeError("a failure has no path")
        if ("equals" in failure) == ("atLeast" in failure) or not _is_number(failure.get("atLeast", 0)):
            raise TypeError("a failure needs exactly one of equals and a numeric atLeast")
        if not all(isinstance(failure.get(key, ""), str) for key in ("message", "code")):
            raise TypeError("a failure's message or code is not a path")
    if not isinstance(rule.get("from", ""), str):
        raise TypeError("from is not a path")
    fields = rule.get("fields") or {}
    if not isinstance(fields, Mapping) or not all(isinstance(path, str) for path in fields.values()):
        raise TypeError("fields is not an object of paths")
    for key in ("omit", "required"):
        names = rule.get(key) or []
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            raise TypeError(f"{key} is not a list of names")
