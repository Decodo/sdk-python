from __future__ import annotations

from typing import Any

import pytest

import decodo
from decodo.codegen.web_scraping_api.generate_targets import _get_targets_file_contents


class TestGeneratedTargetsAll:
    def test_all_lists_every_generated_class_and_union(self, minimal_ir: dict[str, Any]) -> None:
        namespace: dict[str, Any] = {}
        exec(_get_targets_file_contents(minimal_ir["apis"]["webScrapingApi"]), namespace)

        assert namespace["__all__"] == [
            "GoogleSearchParams",
            "GoogleSearchBatchParams",
            "ScrapeRequest",
            "BatchRequest",
            "target_meta",
        ]
        for name in namespace["__all__"]:
            assert name in namespace


@pytest.mark.skipif(not decodo._codegen_available, reason="generated types not present")
class TestPackageExports:
    def test_every_generated_name_is_importable_from_decodo(self) -> None:
        from decodo.generated import parameters, targets

        for name in targets.__all__:
            assert getattr(decodo, name) is getattr(targets, name)
            assert name in decodo.__all__
        for name in ["ParameterMeta", "parameter_meta"]:
            assert getattr(decodo, name) is getattr(parameters, name)
            assert name in decodo.__all__

    def test_target_absent_from_ir_raises_attribute_error(self) -> None:
        with pytest.raises(AttributeError):
            decodo.NoSuchTargetParams  # noqa: B018
