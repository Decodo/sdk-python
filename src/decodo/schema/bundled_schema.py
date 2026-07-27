from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, cast

from decodo.targets import targets

from .build_target_meta import build_target_meta
from .types import DecodoSchema, TargetMeta


def _load_target_meta() -> dict[str, Any] | None:
    try:
        from decodo.generated.targets import target_meta  # noqa: PLC0415
        return cast(dict[str, Any], target_meta)
    except ImportError:
        return None

_target_meta = _load_target_meta()

_IR_JSON_PATH = Path(__file__).parent.parent / "generated" / "decodo.ir.json"


def _load_ir_json() -> dict[str, Any] | None:
    try:
        with open(_IR_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except FileNotFoundError:
        return None


class BundledSchema:
    shared: ClassVar[BundledSchema]

    def __init__(self) -> None:
        ir = _load_ir_json()
        if ir is not None:
            api_targets = ir["apis"]["webScrapingApi"]["targets"]
            self._request_schemas: dict[str, dict[str, Any]] = {
                k: v["parameter_schema"] for k, v in api_targets.items()
            }
            self._target_meta = _target_meta if _target_meta is not None else build_target_meta(api_targets)
        else:
            self._request_schemas = {}
            self._target_meta = _target_meta or {}

    def get_request_schema(self, target: str) -> dict[str, Any] | None:
        return self._request_schemas.get(target)

    def list_targets(self) -> list[str]:
        return list(targets)

    def get_target_meta(self, target: str) -> TargetMeta | None:
        return cast(TargetMeta, self._target_meta.get(target))

    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None:
        return self._request_schemas.get(target)

    def get_shared_parameters(self) -> dict[str, Any]:
        return {}

    @property
    def version(self) -> str | None:
        return None


BundledSchema.shared = BundledSchema()

# Satisfy DecodoSchema protocol
_: DecodoSchema = BundledSchema.shared
