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
