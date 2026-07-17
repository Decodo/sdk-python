from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


MINIMAL_IR_PATH = Path(__file__).parent / "schema" / "fixtures" / "minimal_ir.json"


@pytest.fixture
def minimal_ir() -> dict[str, Any]:
    with open(MINIMAL_IR_PATH, encoding="utf-8") as f:
        return json.load(f)
