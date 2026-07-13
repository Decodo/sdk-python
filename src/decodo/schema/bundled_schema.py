from __future__ import annotations

from typing import Any

from decodo.generated.request_schemas import request_json_schemas
from decodo.generated.targets import target_meta, targets

from .types import DecodoSchema, TargetMeta


class BundledSchema:
    def get_request_schema(self, target: str) -> dict[str, Any] | None:
        return request_json_schemas.get(target)

    def list_targets(self) -> list[str]:
        return list(targets)

    def get_target_meta(self, target: str) -> TargetMeta | None:
        return target_meta.get(target)

    def get_target_parameter_schema(self, target: str) -> dict[str, Any] | None:
        return request_json_schemas.get(target)

    def get_shared_parameters(self) -> dict[str, Any]:
        return {}

    @property
    def version(self) -> str | None:
        return None


BundledSchema.shared: BundledSchema = BundledSchema()  # type: ignore[attr-defined]

# Satisfy DecodoSchema protocol
_: DecodoSchema = BundledSchema.shared  # type: ignore[attr-defined]
