from __future__ import annotations

from contact_finder.matching import names_match
from contact_finder.models import ProviderEvidence
from contact_finder.normalizer import normalize_provider_bundle
from contact_finder.providers import MockProviderLoader
from contact_finder.resolver import (
    collect_sources,
    detect_name_conflict,
    resolve_contact,
)


def _evidence_for(company_name: str):
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    return normalize_provider_bundle(loader.get_for_company(company_name))


def test_resolves_strong_multi_source_match() -> None:
    resolved = resolve_contact(
        "Cedar Ridge Plumbing LLC", _evidence_for("Cedar Ridge Plumbing LLC")
    )

    assert resolved.contact_name == "Daniel Ortega"
    assert resolved.contact_role == "Owner"
    assert resolved.contact_email_or_phone == "d.ortega@cedarridgeplumbing.com"
    assert resolved.confidence_score >= 70
    assert resolved.needs_human_review is False
    assert "registry:mock://registry/ne/cedar-ridge-plumbing" in resolved.source


def test_resolves_two_source_agreement_when_email_supports_person() -> None:
    resolved = resolve_contact("Bayview Auto Repair", _evidence_for("Bayview Auto Repair"))

    assert resolved.contact_name == "Karen Liu"
    assert resolved.contact_role == "Owner"
    assert resolved.contact_email_or_phone == "karen@bayviewauto.com"
    assert resolved.confidence_score >= 70
    assert resolved.needs_human_review is False


def test_generic_weak_enrichment_requires_review_and_blanks_contact_method() -> None:
    resolved = resolve_contact(
        "Riverside Print & Sign", _evidence_for("Riverside Print & Sign")
    )

    assert resolved.confidence_score < 70
    assert resolved.contact_email_or_phone is None
    assert resolved.needs_human_review is True


def test_registry_only_without_contact_method_requires_review() -> None:
    resolved = resolve_contact(
        "Northgate HVAC Services", _evidence_for("Northgate HVAC Services")
    )

    assert resolved.contact_name == "Thomas Reed"
    assert resolved.contact_role == "Registered Agent"
    assert resolved.contact_email_or_phone is None
    assert resolved.needs_human_review is True


def test_conflicting_names_require_review_without_blind_merge() -> None:
    resolved = resolve_contact(
        "Coastal Breeze Pool Service", _evidence_for("Coastal Breeze Pool Service")
    )

    assert resolved.contact_name is None
    assert resolved.contact_role is None
    assert resolved.contact_email_or_phone is None
    assert resolved.needs_human_review is True


def test_missing_provider_response_returns_cannot_verify_result() -> None:
    resolved = resolve_contact("Desert Sky Solar", [])

    assert resolved.company_name == "Desert Sky Solar"
    assert resolved.contact_name is None
    assert resolved.contact_role is None
    assert resolved.contact_email_or_phone is None
    assert resolved.confidence_score < 70
    assert resolved.source == ""
    assert resolved.needs_human_review is True


def test_partial_name_agreement_is_not_a_hard_conflict() -> None:
    harbor_evidence = _evidence_for("Harbor Light Electric")
    ironclad_evidence = _evidence_for("Ironclad Welding Shop")

    assert names_match("Sean Murphy", "S. Murphy") == "soft"
    assert names_match("Robert Kowalski", "Bob Kowalski") == "soft"
    assert detect_name_conflict(harbor_evidence) is False
    assert detect_name_conflict(ironclad_evidence) is False

    resolved = resolve_contact("Harbor Light Electric", harbor_evidence)

    assert resolved.contact_name == "Sean Murphy"
    assert resolved.contact_email_or_phone == "+1-508-555-0160"
    assert resolved.needs_human_review is False


def test_materially_different_full_names_are_conflicts() -> None:
    assert names_match("John Smith", "Jane Smith") == "conflict"
    assert names_match("Tina Alvarez", "Marcus Webb") == "conflict"
    assert names_match("Jeff", "Marcus Webb") == "unknown"


def test_collect_sources_deduplicates_while_preserving_order() -> None:
    evidence = [
        _evidence("registry", "mock://registry/example"),
        _evidence("listing", "mock://listing/example"),
        _evidence("registry", "mock://registry/example"),
    ]

    assert collect_sources(evidence) == (
        "registry:mock://registry/example;listing:mock://listing/example"
    )


def _evidence(provider: str, source_url: str) -> ProviderEvidence:
    return ProviderEvidence(
        provider=provider,
        name=None,
        role=None,
        email=None,
        phone=None,
        provider_confidence=None,
        source_url=source_url,
    )
