from __future__ import annotations

import os
from pathlib import Path

from decodo.schema.expand_path import expand_path


class TestExpandPath:
    def test_expands_tilde_slash_paths_relative_to_home(self) -> None:
        result = expand_path("~/decodo/cache.json")
        expected = str(Path.home() / "decodo" / "cache.json")
        assert result == expected

    def test_expands_tilde_to_home_directory(self) -> None:
        result = expand_path("~")
        assert result == str(Path.home())

    def test_resolves_absolute_paths_unchanged(self) -> None:
        result = expand_path("/tmp/decodo.ir.json")
        assert result == "/tmp/decodo.ir.json"
