from __future__ import annotations

from .types import IrTarget, TargetMeta


def _get_target_parameter_keys(parameter_schema: dict) -> list[str]:
    properties: dict = parameter_schema.get("properties", {})
    return [key for key in properties if key != "target"]


def build_target_meta(targets: dict[str, IrTarget]) -> dict[str, TargetMeta]:
    meta: dict[str, TargetMeta] = {}

    for target_key, target in targets.items():
        meta[target_key] = TargetMeta(
            group=target["group"],
            response_format=target["response_format"],
            parameters=_get_target_parameter_keys(target["parameter_schema"]),
        )

    return meta
