from __future__ import annotations

import json
import os
import re
import warnings
from pathlib import Path

import httpx

from decodo.schema.resolve_latest_ir import resolve_latest_ir

from .types import IR

_THIS_DIR = Path(__file__).parent

local_ir_path = str((_THIS_DIR / "../../../.." / "inputs" / "decodo.ir.json").resolve())
out_dir = str((_THIS_DIR / "../../generated").resolve())


def to_pascal_case(s: str) -> str:
    s = re.sub(r"([a-z])([A-Z])", r"\1_\2", s)
    parts = re.split(r"[_\s-]+", s)
    return "".join(w[0].upper() + w[1:].lower() for w in parts if w)


def to_enum_member_name(target_key: str) -> str:
    pascal = to_pascal_case(target_key)
    if re.match(r"^[0-9]", pascal) or not re.match(r"^[A-Za-z_]", pascal):
        return f"_{pascal}"
    return pascal


def prop_key(key: str) -> str:
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
        return key
    return json.dumps(key)


def fetch_intermediate_representation() -> IR:
    try:
        location = resolve_latest_ir()
        url = location["url"]
        response = httpx.get(url)
        if not response.is_success:
            raise RuntimeError(f"HTTP {response.status_code}")
        raw = response.text
        os.makedirs(os.path.dirname(local_ir_path), exist_ok=True)
        with open(local_ir_path, "w", encoding="utf-8") as f:
            f.write(raw)
        return json.loads(raw)
    except Exception as err:
        message = str(err)
        if os.path.exists(local_ir_path):
            warnings.warn(
                f"Warning: failed to fetch IR ({message}). Using cached local file.",
                stacklevel=2,
            )
            with open(local_ir_path, encoding="utf-8") as f:
                return json.load(f)
        raise RuntimeError(
            f"Failed to fetch IR ({message}) and no local cache found at {local_ir_path}."
        ) from None
