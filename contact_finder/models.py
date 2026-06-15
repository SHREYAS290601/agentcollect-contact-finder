from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyInput:
    company_name: str
    mailing_address: str


@dataclass(frozen=True)
class ProviderEvidence:
    provider: str
    name: str | None
    role: str | None
    email: str | None
    phone: str | None
    provider_confidence: int | None
    source_url: str | None


@dataclass(frozen=True)
class ResolvedContact:
    company_name: str
    contact_name: str | None
    contact_role: str | None
    contact_email_or_phone: str | None
    confidence_score: int
    source: str
    needs_human_review: bool
