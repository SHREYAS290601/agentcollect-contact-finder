from __future__ import annotations

from contact_finder.matching import is_generic_email, names_match, normalize_name
from contact_finder.models import ProviderEvidence


def score_contact(
    evidence: list[ProviderEvidence],
    has_conflict: bool,
    chosen_contact_method: str | None,
    chosen_role: str | None,
    chosen_name: str | None,
) -> int:
    if not evidence:
        return 0

    useful_evidence = [
        item
        for item in evidence
        if item.name
        or item.role
        or item.email
        or item.phone
        or item.provider_confidence is not None
    ]

    score = 10
    provider_count = len({item.provider for item in useful_evidence})
    if provider_count >= 3:
        score += 25
    elif provider_count == 2:
        score += 18
    else:
        score -= 15

    if not has_conflict:
        name_agreement = _name_agreement(useful_evidence)
        if name_agreement == "exact":
            score += 20
        elif name_agreement == "soft":
            score += 15

    if _has_phone_agreement(useful_evidence):
        score += 12

    score += _role_points(chosen_role)

    if chosen_contact_method:
        score += 15
        if "@" in chosen_contact_method:
            if is_generic_email(chosen_contact_method):
                score -= 18
            else:
                score += 12
    else:
        score -= 20

    score += _enrichment_confidence_points(useful_evidence)

    if has_conflict:
        score -= 40

    if any(is_generic_email(item.email) for item in useful_evidence if item.email):
        score -= 8

    if not any(item.email or item.phone for item in useful_evidence):
        score -= 30

    if _registered_agent_without_contact(useful_evidence):
        score -= 15

    return max(0, min(100, score))


def _name_agreement(evidence: list[ProviderEvidence]) -> str:
    names = [item.name for item in evidence if item.name]
    if len(names) < 2:
        return "none"

    pair_results = [
        names_match(name, other_name)
        for index, name in enumerate(names)
        for other_name in names[index + 1 :]
    ]
    if "conflict" in pair_results:
        return "none"

    normalized = {normalize_name(name) for name in names}
    if len(normalized) == 1:
        return "exact"

    if "soft" in pair_results:
        return "soft"

    return "none"


def _has_phone_agreement(evidence: list[ProviderEvidence]) -> bool:
    listing_phones = {item.phone for item in evidence if item.provider == "listing" and item.phone}
    enrichment_phones = {
        item.phone for item in evidence if item.provider == "enrichment" and item.phone
    }
    return bool(listing_phones & enrichment_phones)


def _role_points(role: str | None) -> int:
    normalized_role = (role or "").casefold()
    normalized_role = normalized_role.replace("/", " ")
    role_tokens = {token.strip(".,()") for token in normalized_role.split()}

    if (
        "accounts payable" in normalized_role
        or "ap manager" in normalized_role
        or role_tokens == {"ap"}
        or ("ap" in role_tokens and "manager" in role_tokens)
    ):
        return 15
    if any(
        term in normalized_role
        for term in ("owner", "founder", "president", "cfo", "finance")
    ):
        return 12
    if "office manager" in normalized_role or "manager" in role_tokens:
        return 6
    return 0


def _enrichment_confidence_points(evidence: list[ProviderEvidence]) -> int:
    confidences = [
        item.provider_confidence
        for item in evidence
        if item.provider == "enrichment" and item.provider_confidence is not None
    ]
    if not confidences:
        return 0

    confidence = max(confidences)
    if confidence >= 80:
        return 12
    if confidence >= 70:
        return 8
    if confidence >= 50:
        return 2
    return -8


def _registered_agent_without_contact(evidence: list[ProviderEvidence]) -> bool:
    has_registered_agent = any(
        item.role and item.role.casefold() == "registered agent" for item in evidence
    )
    has_contact_method = any(item.email or item.phone for item in evidence)
    return has_registered_agent and not has_contact_method


