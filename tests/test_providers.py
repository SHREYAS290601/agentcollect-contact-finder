from __future__ import annotations

import pytest

from contact_finder.providers import MockProviderLoader


def test_loader_returns_data_for_known_company() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")

    bundle = loader.get_for_company("Cedar Ridge Plumbing LLC")

    assert bundle is not None
    assert bundle["registry"]["name"] == "Daniel Ortega"


def test_loader_returns_none_for_unknown_company() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")

    assert loader.get_for_company("Unknown Company") is None


def test_invalid_json_raises_clear_error(tmp_path) -> None:
    invalid_json_path = tmp_path / "invalid.json"
    invalid_json_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid mock provider JSON"):
        MockProviderLoader(invalid_json_path)
