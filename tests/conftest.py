from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import decodo.schema.bundled_schema as _bundled_schema_mod

MINIMAL_IR_PATH = Path(__file__).parent / "schema" / "fixtures" / "minimal_ir.json"


@pytest.fixture(autouse=True, scope="session")
def _patch_bundled_schema_ir_path() -> None:
    _bundled_schema_mod._BUNDLED_IR_PATH = MINIMAL_IR_PATH
    _bundled_schema_mod.BundledSchema.shared = _bundled_schema_mod.BundledSchema()


@pytest.fixture
def minimal_ir() -> dict[str, Any]:
    with open(MINIMAL_IR_PATH, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]
