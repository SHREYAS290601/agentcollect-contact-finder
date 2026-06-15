from __future__ import annotations

from contact_finder.matching import (
    email_matches_name,
    is_generic_email,
    names_match,
    normalize_name,
)
from contact_finder.models import ProviderEvidence, ResolvedContact
from contact_finder.scorer import score_contact


REVIEW_THRESHOLD = 70


def resolve_contact(company_name: str, evidence: list[ProviderEvidence]) -> ResolvedContact:
    sources = collect_sources(evidence)
    if not evidence:
        return ResolvedContact(
            company_name=company_name,
            contact_name=None,
            contact_role=None,
            contact_email_or_phone=None,
            confidence_score=0,
            source=sources,
            needs_human_review=True,
        )

    has_conflict = detect_name_conflict(evidence)
    chosen_name = None if has_conflict else _choose_name(evidence)
    chosen_role = _choose_role(evidence, chosen_name)
    chosen_method = None if has_conflict else _choose_contact_method(evidence, chosen_name)

    if chosen_method and chosen_name is None:
        chosen_role = "business_contact"

    confidence_score = score_contact(
        evidence=evidence,
        has_conflict=has_conflict,
        chosen_contact_method=chosen_method,
        chosen_role=chosen_role,
        chosen_name=chosen_name,
    )
    needs_human_review = has_conflict or confidence_score < REVIEW_THRESHOLD
    emitted_method = chosen_method if not needs_human_review else None

    return ResolvedContact(
        company_name=company_name,
        contact_name=chosen_name,
        contact_role=chosen_role,
        contact_email_or_phone=emitted_method,
        confidence_score=confidence_score,
        source=sources,
        needs_human_review=needs_human_review,
    )


def detect_name_conflict(evidence: list[ProviderEvidence]) -> bool:
    names = [item.name for item in evidence if normalize_name(item.name)]
    for index, name in enumerate(names):
        for other_name in names[index + 1 :]:
            if names_match(name, other_name) == "conflict":
                return True
    return False


def collect_sources(evidence: list[ProviderEvidence]) -> str:
    sources: list[str] = []
    seen_sources: set[str] = set()
    for item in evidence:
        if not item.source_url:
            continue

        source = f"{item.provider}:{item.source_url}"
        if source in seen_sources:
            continue

        sources.append(source)
        seen_sources.add(source)

    return ";".join(sources)


def _choose_name(evidence: list[ProviderEvidence]) -> str | None:
    named_evidence = [item for item in evidence if item.name]
    if not named_evidence:
        return None

    registry_name = next((item.name for item in named_evidence if item.provider == "registry"), None)
    if registry_name:
        return registry_name
    return named_evidence[0].name


def _choose_role(evidence: list[ProviderEvidence], chosen_name: str | None) -> str | None:
    if chosen_name is None:
        return None

    for item in evidence:
        if item.role and names_match(item.name, chosen_name) in {"exact", "soft"}:
            return item.role
    return None


def _choose_contact_method(
    evidence: list[ProviderEvidence], chosen_name: str | None
) -> str | None:
    email = _choose_email(evidence, chosen_name)
    if email:
        return email

    return _choose_phone(evidence, chosen_name)


def _choose_email(evidence: list[ProviderEvidence], chosen_name: str | None) -> str | None:
    emails = [item.email for item in evidence if item.email]
    if chosen_name:
        for email in emails:
            if not is_generic_email(email) and email_matches_name(email, chosen_name):
                return email
        return None

    for email in emails:
        if not is_generic_email(email):
            return email
    return emails[0] if emails else None


def _choose_phone(evidence: list[ProviderEvidence], chosen_name: str | None) -> str | None:
    if chosen_name:
        for item in evidence:
            if item.phone and names_match(item.name, chosen_name) in {"exact", "soft"}:
                return item.phone
        for item in evidence:
            if item.phone and item.email and email_matches_name(item.email, chosen_name):
                return item.phone
        return None

    phone_counts: dict[str, int] = {}
    for item in evidence:
        if item.phone:
            phone_counts[item.phone] = phone_counts.get(item.phone, 0) + 1

    for phone, count in phone_counts.items():
        if count > 1:
            return phone

    return next((item.phone for item in evidence if item.phone), None)

