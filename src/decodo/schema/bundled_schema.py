from __future__ import annotations

import json
import os
import warnings
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

_BUNDLED_IR_PATH = Path(__file__).parent.parent / "generated" / "decodo.ir.json"


def _find_ir_path() -> Path | None:
    env = os.environ.get("DECODO_IR_PATH")
    if env:
        p = Path(env)
        if p.is_file():
            return p
    local = Path.cwd() / "decodo_generated" / "decodo.ir.json"
    if local.is_file():
        return local
    if _BUNDLED_IR_PATH.is_file():
        return _BUNDLED_IR_PATH
    return None


def _load_ir_json() -> dict[str, Any] | None:
    path = _find_ir_path()
    if path is None:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except (OSError, json.JSONDecodeError):
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
            warnings.warn(
                "Decodo IR schema not found — payload validation is disabled. "
                "Run: python -m decodo.codegen.codegen (editable install) or "
                "python -m decodo.codegen.codegen --out-dir ./decodo_generated (pip install).",
                RuntimeWarning,
                stacklevel=2,
            )
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
