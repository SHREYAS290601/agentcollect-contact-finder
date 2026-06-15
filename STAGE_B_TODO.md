# Stage B — Contact Finder TODO

Minimal slice: read `challenge/data/companies.csv`, resolve one contact per company from mock providers, write output with provenance and review flags.

---

## 1. Required output fields

Per input row (one row out per row in):

| Field | Notes |
|-------|-------|
| `contact_name` | Person name when supported; empty if only generic/business-level contact |
| `contact_role` | From provider evidence when supported; use generic `business_contact` only for clearly company-level contacts; otherwise empty |
| `contact_email_or_phone` | Single best reachable method; **empty when confidence &lt; 70** |
| `confidence_score` | 0–100, our logic (not raw `provider_confidence`) |
| `source` | Provenance: which provider(s) and `source_url`(s) contributed |
| `needs_human_review` | `true` when confidence &lt; 70, conflicts, or cannot verify |

Also carry through required `company_name` for traceability; optional `mailing_address` may be included for debugging.

---

## 2. Clarification-driven rules

- **Mock only** — load from `challenge/mocks/enrichment_responses.json`; no real APIs, no scraping.
- **One good contact per company** is enough; do not emit multiple candidates.
- **Precision over recall** — prefer empty + review over a guess.
- **Threshold 70** — if `confidence_score < 70`: `contact_email_or_phone = ""` and `needs_human_review = true`.
- **Provenance required** — every non-empty value must trace to at least one `mock://…` `source_url`; never invent data.
- **Business contacts only** — US B2B; no personal/home data; support opt-out/suppression hook in design (even if unused in mocks).

**Role priority** (when choosing among candidates): AP manager → owner/founder (small biz) → CFO/finance lead → office manager → registered agent / manager (lower).

---

## 3. Provider lookup workflow

```
companies.csv row
  → exact match on company_name
  → enrichment_responses.json[company_name]
  → per-provider sections: registry | listing | enrichment
```

- Missing company key → all providers not-found (not an error).
- Missing provider section (e.g. only `listing` present) → that provider not-found.
- `null` fields within a provider → that field absent for that source.
- Normalize each provider payload into a common **evidence** shape before resolution.

---

## 4. Contact resolution scenarios (from mocks)

Map each pattern to expected behavior in tests:

| Scenario | Example company | Expected handling |
|----------|-----------------|-------------------|
| **Strong multi-source agreement** | Cedar Ridge Plumbing, Pioneer Landscaping, Brookside Veterinary | High confidence; name + role + email/phone; multiple `source_url`s in `source` |
| **Two-source agreement** | Bayview Auto Repair, Tidewater Plumbing, Greenfield Catering | Good confidence if name/phone align; emit contact if ≥ 70 |
| **Generic email only** | Riverside Print (`info@…`), Summit Pest (`contact@…`), Hometown Hardware | Low confidence; penalize generic prefix; likely review + empty contact |
| **Listing-only phone** | Maple Leaf Bakery | Phone from listing only; no person name → weak; likely review unless strong role fit |
| **Registry-only, no contact method** | Northgate HVAC (Registered Agent) | May retain name/role; **no email/phone** → empty contact, review |
| **Conflicting names** | Coastal Breeze (Tina vs Marcus), Lakeside Auto Glass (Jeff vs listing) | Penalize; `needs_human_review = true`; do not merge blindly |
| **Missing provider response** | Desert Sky Solar, Cornerstone Masonry, + 10 other CSV rows absent from JSON | Cannot verify; empty contact fields, low confidence, review |

**Partial-name agreement** (Harbor Light: Sean Murphy / S. Murphy; Ironclad: Robert / Bob): treat as soft match with modest boost, not full agreement.

**Conflict safety:** do not combine one provider's person name with another provider's unrelated phone/email unless identity match is supported.

**Single weak enrichment** (Anchor Marine `sales@…`, provider_confidence 63): our score should land below 70.

---

## 5. Confidence scoring rules

Explainable additive model (tune weights in implementation):

**Increase confidence**
- +N per **independent agreeing source** (name match across registry + listing + enrichment)
- +role fit: Owner / President / CFO / AP manager &gt; Manager &gt; Registered Agent
- +person-specific email (e.g. `d.ortega@…`, `maria@…`) vs generic (`info@`, `office@`, `contact@`, `sales@`)
- +phone agreement across listing and enrichment

**Decrease confidence**
- Generic / role-less business email
- Single source only (especially enrichment-only)
- Low `enrichment.provider_confidence` (&lt; 50)
- Name conflict across sources
- Registered agent with no direct contact method
- No email and no phone in evidence

**Hard gates**
- No email **and** no phone → cannot emit usable `contact_email_or_phone` (score effectively &lt; 70)
- Material name conflict → force `needs_human_review` even if contact method exists
- `enrichment.provider_confidence` is one input signal, **not** the final score

---

## 6. Proposed Laravel file structure (minimal slice)

Follow existing `app/Modules/` convention; CLI entry via Artisan.

```
app/Modules/ContactFinder/
  Data/
    CompanyInput.php          # company_name, mailing_address
    ProviderEvidence.php      # normalized per-provider facts + source_url
    ResolvedContact.php       # output DTO
  Services/
    CompanyCsvReader.php      # read challenge/data/companies.csv
    MockProviderLoader.php    # JSON lookup by exact company_name
    EvidenceNormalizer.php    # registry | listing | enrichment → ProviderEvidence[]
    ContactResolver.php       # pick name, role, email/phone; detect conflicts
    ConfidenceScorer.php      # 0–100 + review flag
    ContactOutputWriter.php   # write CSV/JSON to storage/app/contact_finder/
app/Console/Commands/
  ResolveContactsCommand.php  # artisan contact-finder:resolve [--limit=N]
config/contact_finder.php     # paths to CSV + mock JSON (optional)
tests/Unit/Modules/ContactFinder/
  MockProviderLoaderTest.php
  EvidenceNormalizerTest.php
  ContactResolverTest.php
  ConfidenceScorerTest.php
  ResolveContactsCommandTest.php
```

No new DB tables, HTTP routes, or queue jobs for this slice.

---

## 7. Implementation commit plan

| # | Commit | Scope |
|---|--------|-------|
| 1 | Add Stage B TODOs | This file |
| 2 | Provider loader + evidence normalization | `MockProviderLoader`, `EvidenceNormalizer`, DTOs, `CompanyCsvReader` |
| 3 | Contact resolver + confidence scorer | `ContactResolver`, `ConfidenceScorer`, role priority + conflict detection |
| 4 | Output writer + Artisan command | `ContactOutputWriter`, `ResolveContactsCommand`, config paths |
| 5 | Tests | Unit tests for each scenario in §4; command integration test |
| 6 | Docs | `ABOUT.md` (from template), brief usage note in README or command `--help` |

**Slice scope:** process all 30 CSV rows (or `--limit` for dev); 18 have mock data, 12 exercise not-found paths.

**Assumptions** (not in clarifications): output format = CSV with header; `source` field = semicolon-separated `provider:mock://url` pairs; name fuzzy-match uses simple normalization (lowercase, strip titles/parens, initial expansion) — document in scorer.
