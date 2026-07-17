from __future__ import annotations

import pytest

from decodo.schema.bundled_schema import BundledSchema


class TestBundledSchemaShared:
    def setup_method(self) -> None:
        self.schema = BundledSchema.shared

    def test_lists_bundled_targets(self) -> None:
        targets = self.schema.list_targets()
        assert len(targets) > 0
        assert "google_search" in targets

    def test_returns_target_metadata_for_known_target(self) -> None:
        meta = self.schema.get_target_meta("google_search")

        assert meta is not None
        assert meta["group"] == "Google"
        assert "query" in meta["parameters"]

    def test_validates_request_payloads_for_known_target(self) -> None:
        import jsonschema

        schema = self.schema.get_request_schema("google_search")
        assert schema is not None

        jsonschema.validate(
            {"target": "google_search", "query": "coffee"},
            schema,
        )

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(
                {"target": "google_search", "page_from": -1},
                schema,
            )

    def test_returns_json_parameter_schema_for_known_target(self) -> None:
        param_schema = self.schema.get_target_parameter_schema("google_search")
        assert param_schema is not None
        assert "query" in param_schema.get("properties", {})

    def test_returns_empty_shared_parameters(self) -> None:
        assert self.schema.get_shared_parameters() == {}
