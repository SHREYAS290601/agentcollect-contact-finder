from __future__ import annotations

from typing import Any

from contact_finder.models import ProviderEvidence


def normalize_provider_bundle(bundle: dict | None) -> list[ProviderEvidence]:
    if bundle is None:
        return []

    evidence: list[ProviderEvidence] = []

    registry = _section(bundle, "registry")
    if registry is not None:
        evidence.append(
            ProviderEvidence(
                provider="registry",
                name=registry.get("name"),
                role=registry.get("role"),
                email=None,
                phone=None,
                provider_confidence=None,
                source_url=registry.get("source_url"),
            )
        )

    listing = _section(bundle, "listing")
    if listing is not None:
        evidence.append(
            ProviderEvidence(
                provider="listing",
                name=listing.get("name"),
                role=None,
                email=None,
                phone=listing.get("phone"),
                provider_confidence=None,
                source_url=listing.get("source_url"),
            )
        )

    enrichment = _section(bundle, "enrichment")
    if enrichment is not None:
        evidence.append(
            ProviderEvidence(
                provider="enrichment",
                name=None,
                role=None,
                email=enrichment.get("email"),
                phone=enrichment.get("phone"),
                provider_confidence=enrichment.get("provider_confidence"),
                source_url=enrichment.get("source_url"),
            )
        )

    return evidence


def _section(bundle: dict[str, Any], provider: str) -> dict[str, Any] | None:
    section = bundle.get(provider)
    if section is None:
        return None
    if not isinstance(section, dict):
        raise ValueError(f"Provider section must be an object: {provider}")
    return section
