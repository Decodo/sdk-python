from __future__ import annotations

import os
from pathlib import Path


def expand_path(path: str) -> str:
    if path.startswith("~/"):
        return str(Path.home() / path[2:])
    if path == "~":
        return str(Path.home())
    return os.path.abspath(path)
