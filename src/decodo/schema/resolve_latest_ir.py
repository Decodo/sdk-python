from __future__ import annotations

import re

import httpx

from .constants import DEFAULT_IR_BASE, DEFAULT_IR_LIST_URL, DEFAULT_IR_PREFIX
from .types import GcsObjectList, LatestIrLocation

_IR_OBJECT_PATTERN = re.compile(r"^decodo-ir-v(.+)\.json$")


def _parse_semver(version: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _compare_semver(left: str, right: str) -> int:
    parsed_left = _parse_semver(left)
    parsed_right = _parse_semver(right)

    if parsed_left is None or parsed_right is None:
        if left < right:
            return -1
        if left > right:
            return 1
        return 0

    for l, r in zip(parsed_left, parsed_right):
        if l != r:
            return l - r

    return 0


def _parse_ir_versions(names: list[str]) -> list[str]:
    versions: list[str] = []
    for name in names:
        match = _IR_OBJECT_PATTERN.match(name)
        if match and _parse_semver(match.group(1)):
            versions.append(match.group(1))
    return versions


def resolve_latest_ir() -> LatestIrLocation:
    response = httpx.get(DEFAULT_IR_LIST_URL, headers={"Accept": "application/json"})

    if not response.is_success:
        raise RuntimeError(
            f"Failed to list IR versions from {DEFAULT_IR_LIST_URL}: HTTP {response.status_code}"
        )

    body: GcsObjectList = response.json()
    names = [item["name"] for item in body.get("items", [])]
    versions = _parse_ir_versions(names)

    if not versions:
        raise RuntimeError(
            f'No versioned IR objects found in bucket with prefix "{DEFAULT_IR_PREFIX}".'
        )

    version = max(versions, key=lambda v: _parse_semver(v) or (0, 0, 0))

    return LatestIrLocation(
        version=version,
        url=f"{DEFAULT_IR_BASE}/{DEFAULT_IR_PREFIX}{version}.json",
    )
