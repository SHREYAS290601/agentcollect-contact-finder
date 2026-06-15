from __future__ import annotations

from contact_finder.normalizer import normalize_provider_bundle
from contact_finder.providers import MockProviderLoader


def test_normalizes_registry_listing_and_enrichment_evidence() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    bundle = loader.get_for_company("Cedar Ridge Plumbing LLC")

    evidence = normalize_provider_bundle(bundle)
    by_provider = {item.provider: item for item in evidence}

    assert set(by_provider) == {"registry", "listing", "enrichment"}
    assert by_provider["registry"].name == "Daniel Ortega"
    assert by_provider["registry"].role == "Owner"
    assert by_provider["listing"].name == "Daniel Ortega"
    assert by_provider["listing"].phone == "+1-402-555-0148"
    assert by_provider["enrichment"].email == "d.ortega@cedarridgeplumbing.com"
    assert by_provider["enrichment"].provider_confidence == 84


def test_missing_provider_sections_do_not_crash() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    bundle = loader.get_for_company("Bayview Auto Repair")

    evidence = normalize_provider_bundle(bundle)

    assert [item.provider for item in evidence] == ["registry", "enrichment"]


def test_none_bundle_returns_empty_list() -> None:
    assert normalize_provider_bundle(None) == []


def test_null_fields_remain_none() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    bundle = loader.get_for_company("Maple Leaf Bakery")

    evidence = normalize_provider_bundle(bundle)

    assert len(evidence) == 1
    assert evidence[0].provider == "listing"
    assert evidence[0].name is None
    assert evidence[0].role is None
    assert evidence[0].email is None
    assert evidence[0].provider_confidence is None


def test_source_url_is_preserved_where_present() -> None:
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    bundle = loader.get_for_company("Cedar Ridge Plumbing LLC")

    evidence = normalize_provider_bundle(bundle)
    source_urls = {item.provider: item.source_url for item in evidence}

    assert source_urls == {
        "registry": "mock://registry/ne/cedar-ridge-plumbing",
        "listing": "mock://listing/cedar-ridge-plumbing",
        "enrichment": "mock://enrichment/cedar-ridge-plumbing",
    }
