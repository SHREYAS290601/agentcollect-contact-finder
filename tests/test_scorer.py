from __future__ import annotations

from contact_finder.matching import is_generic_email, names_match
from contact_finder.normalizer import normalize_provider_bundle
from contact_finder.models import ProviderEvidence
from contact_finder.providers import MockProviderLoader
from contact_finder.resolver import detect_name_conflict, resolve_contact
from contact_finder.scorer import _name_agreement, score_contact


def _evidence_for(company_name: str):
    loader = MockProviderLoader("challenge/mocks/enrichment_responses.json")
    return normalize_provider_bundle(loader.get_for_company(company_name))


def test_score_is_high_for_strong_multi_source_match() -> None:
    evidence = _evidence_for("Pioneer Landscaping Inc")

    score = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method="maria@pioneerlandscaping.com",
        chosen_role="President",
        chosen_name="Maria Gomez",
    )

    assert score >= 70


def test_score_is_high_for_supported_two_source_match() -> None:
    evidence = _evidence_for("Tidewater Plumbing & Heating")

    score = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method="g.whitfield@tidewaterph.com",
        chosen_role="Owner",
        chosen_name="George Whitfield",
    )

    assert score >= 70


def test_generic_single_source_enrichment_scores_below_threshold() -> None:
    evidence = _evidence_for("Summit Pest Control")

    score = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method="contact@summitpest.io",
        chosen_role="business_contact",
        chosen_name=None,
    )

    assert score < 70


def test_no_email_or_phone_scores_below_threshold() -> None:
    evidence = _evidence_for("Northgate HVAC Services")

    score = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method=None,
        chosen_role="Registered Agent",
        chosen_name="Thomas Reed",
    )

    assert score < 70


def test_conflict_penalty_forces_review_even_with_phone_evidence() -> None:
    evidence = _evidence_for("Coastal Breeze Pool Service")
    resolved = resolve_contact("Coastal Breeze Pool Service", evidence)

    assert detect_name_conflict(evidence) is True
    assert resolved.needs_human_review is True
    assert resolved.contact_email_or_phone is None


def test_threshold_rule_blanks_contact_method_below_70() -> None:
    resolved = resolve_contact("Anchor Marine Supply", _evidence_for("Anchor Marine Supply"))

    assert resolved.confidence_score < 70
    assert resolved.contact_email_or_phone is None
    assert resolved.needs_human_review is True


def test_private_name_matcher_uses_conservative_rules() -> None:
    assert names_match("Daniel Ortega", "Daniel Ortega") == "exact"
    assert names_match("Sean Murphy", "S. Murphy") == "soft"
    assert names_match("Robert Kowalski", "Bob Kowalski") == "soft"
    assert names_match("John Smith", "Jane Smith") == "conflict"
    assert names_match("Tina Alvarez", "Marcus Webb") == "conflict"
    assert names_match("Jeff", "Marcus Webb") == "unknown"


def test_name_agreement_returns_none_when_any_pair_conflicts() -> None:
    evidence = [
        _evidence(provider="registry", name="John Smith"),
        _evidence(provider="listing", name="John Smith"),
        _evidence(provider="enrichment", name="Jane Smith"),
    ]

    assert _name_agreement(evidence) == "none"


def test_conflict_score_does_not_receive_name_agreement_bonus() -> None:
    evidence = [
        _evidence(provider="registry", name="John Smith", role="Owner"),
        _evidence(provider="listing", name="Jane Smith", phone="+1-555-0100"),
    ]

    score = score_contact(
        evidence=evidence,
        has_conflict=True,
        chosen_contact_method="+1-555-0100",
        chosen_role="Owner",
        chosen_name="John Smith",
    )

    assert score < 70


def test_missing_chosen_contact_method_lowers_score() -> None:
    evidence = _evidence_for("Pioneer Landscaping Inc")

    with_method = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method="maria@pioneerlandscaping.com",
        chosen_role="President",
        chosen_name="Maria Gomez",
    )
    without_method = score_contact(
        evidence=evidence,
        has_conflict=False,
        chosen_contact_method=None,
        chosen_role="President",
        chosen_name="Maria Gomez",
    )

    assert without_method < with_method


def test_provider_coverage_counts_only_useful_evidence() -> None:
    useful_only = [_evidence(provider="registry", name="Daniel Ortega", role="Owner")]
    with_empty_provider = [
        *useful_only,
        _evidence(provider="listing", source_url="mock://listing/empty"),
    ]

    assert score_contact(
        evidence=with_empty_provider,
        has_conflict=False,
        chosen_contact_method=None,
        chosen_role="Owner",
        chosen_name="Daniel Ortega",
    ) == score_contact(
        evidence=useful_only,
        has_conflict=False,
        chosen_contact_method=None,
        chosen_role="Owner",
        chosen_name="Daniel Ortega",
    )


def test_billing_email_prefix_is_not_hard_generic() -> None:
    assert is_generic_email("billing@example.com") is False
    assert is_generic_email("support@example.com") is True


def _evidence(
    provider: str,
    name: str | None = None,
    role: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    provider_confidence: int | None = None,
    source_url: str | None = None,
) -> ProviderEvidence:
    return ProviderEvidence(
        provider=provider,
        name=name,
        role=role,
        email=email,
        phone=phone,
        provider_confidence=provider_confidence,
        source_url=source_url,
    )
