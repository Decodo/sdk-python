from __future__ import annotations

from decodo.schema.build_target_meta import build_target_meta
from decodo.schema.types import IrTarget


class TestBuildTargetMeta:
    def test_builds_group_response_format_and_parameter_names_excluding_target(self) -> None:
        targets: dict[str, IrTarget] = {
            "google_search": IrTarget(
                group="Google",
                response_format="json",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "const": "google_search"},
                        "query": {"type": "string"},
                        "parse": {"type": "boolean"},
                    },
                    "required": ["target", "query"],
                },
            )
        }

        meta = build_target_meta(targets)

        assert meta["google_search"] == {
            "group": "Google",
            "response_format": "json",
            "parameters": ["query", "parse"],
        }
