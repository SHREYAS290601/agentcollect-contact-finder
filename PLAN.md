# PLAN.md

## 1. Problem understanding

We have company records with only `company_name` and `mailing_address`. The goal is to identify a reachable business contact with payment, ownership, finance, operations, or administrative responsibility.

Not every company will have a verifiable contact. The system should preserve source provenance, avoid invented contacts, and clearly mark uncertain or cannot-verify outcomes for human review.

## 2. Proposed architecture

Input company records
→ source lookup layer
→ evidence normalization
→ contact candidate extraction
→ entity matching and deduplication
→ confidence scoring
→ human-review gate
→ final output writer

The lookup layer should use only an allowed source/provider interface. Evidence is normalized into a common shape, candidates are extracted and matched back to the input company, duplicates are merged, confidence is scored, and only sufficiently supported results are written out.

## 3. Source strategy

Use multiple approved source types because no single source will be complete or always current:

- Approved business identity sources to confirm the company entity
- Approved business listing/contact sources to find business-level contact methods
- Approved contact enrichment or account-history sources, if supplied
- Challenge-provided data or provider interface for implementation

The design should keep source adapters separate from matching, scoring, and output logic.

## 4. Contact resolution strategy

For each company record, normalize the company identity, gather allowed evidence, extract contact candidates, match them back to the company, deduplicate overlapping candidates, and rank by confidence.

Prefer contacts with clear payment authority or business decision responsibility, then general business contacts only if policy allows. Never invent a person, title, email pattern, or phone number. If only a company-level contact is supported, label it that way.

## 5. Confidence scoring approach

Confidence should be transparent and explainable. Signals should include:

- Company match quality
- Role or responsibility fit
- Contactability of the email or phone
- Source reliability and provenance
- Agreement across sources
- Freshness, when available
- Penalties for conflicts, stale evidence, or weak company linkage

Use qualitative bands until the implementation policy defines exact cutoffs: High confidence, Medium confidence, Low confidence, and Cannot verify.

## 6. Human review / cannot-verify handling

Route a record to human review when no candidate is found, confidence is too weak under the implementation review policy, sources conflict, provenance is missing, or compliance concerns appear.

Cannot-verify is a valid outcome, not a failure. Those rows should remain in the output with empty or clearly marked contact fields, low confidence, available source notes, and a clear review status.

## 7. Quality checks

- Validate required input fields
- Normalize company names, addresses, phones, emails, and domains before matching
- Preserve source provenance for every returned value
- Deduplicate exact and near-duplicate candidates
- Penalize common-name matches without strong company linkage
- Treat not-found outcomes as first-class results
- Prefer precision over coverage when evidence is weak
- Route uncertain or conflicting records to human review

## 8. Privacy and compliance

- Use only allowed sources and supplied data/provider interfaces
- Do not scrape real websites or bypass access controls
- Do not infer private personal emails from name patterns
- Collect only data needed for business payment outreach
- Respect opt-out, suppression, and do-not-contact rules if provided
- Prefer business contact channels over personal ones unless policy explicitly allows otherwise
- Avoid logging or exposing unnecessary personal data

## 9. Clarifying questions

Question: What false-positive rate is acceptable?
Why it matters: A wrong contact can damage trust and create compliance risk.
Default assumption: Optimize for high precision and route uncertainty to review.
Design impact: Lower tolerance means stricter scoring and less automated coverage.

Question: Are generic business emails or phones acceptable?
Why it matters: Small businesses may not publish named contacts.
Default assumption: Accept them only when clearly tied to the company and labeled as business-level contacts.
Design impact: If not acceptable, more rows become cannot-verify or human-review outcomes.

Question: Which contact responsibilities should be preferred?
Why it matters: Outreach quality depends on reaching someone who can resolve payment.
Default assumption: Prefer contacts with clear payment authority or business decision responsibility, then general business contacts only if policy allows.
Design impact: This changes candidate ranking and review behavior.

Question: How should conflicting sources be handled?
Why it matters: Sources may disagree on company identity, contact, role, or contact method.
Default assumption: Penalize conflicts and route material disagreements to review.
Design impact: A trusted source hierarchy would allow more automatic resolution.

Question: What output format is required?
Why it matters: The final writer should match downstream evaluation or ingestion.
Default assumption: One row per input company with contact fields, confidence, provenance, and review status.
Design impact: Format requirements affect field names, null handling, and validation.

Question: How fresh must evidence be?
Why it matters: Small-business staff, ownership, and contact methods can change.
Default assumption: Prefer recent evidence and penalize stale or undated evidence.
Design impact: Stricter freshness rules increase human-review volume.

Question: What opt-out or compliance requirements apply?
Why it matters: Some contacts or companies may be suppressed regardless of match quality.
Default assumption: Suppression signals override enrichment and outreach.
Design impact: Compliance checks become a pre-output gate.

Question: Should we optimize for precision or coverage?
Why it matters: Higher coverage increases the risk of false positives.
Default assumption: Favor precision when evidence is weak.
Design impact: Precision-first behavior raises review rates; coverage-first behavior may allow more single-source or generic contacts.

## 10. Risks and tradeoffs

- Conservative scoring protects trust but leaves more unresolved companies
- Generic contacts may be useful but less targeted than verified named contacts
- Stale or conflicting evidence can create false positives
- Common names are easy to misattribute without strong company linkage
- Compliance limits may reduce coverage but are necessary
- Challenge-data scope may not reflect full production complexity

## 11. Post-plan implementation approach

After this Stage A plan is committed, read the next-stage instructions and adjust implementation assumptions, scoring policy, output requirements, and contact preferences accordingly.

Build the smallest useful pipeline: read company records, call the allowed source/provider interface, normalize evidence, extract and deduplicate candidates, score confidence, apply the human-review gate, and write final results with provenance. Add focused checks for found, not-found, low-confidence, generic-contact, duplicate, and conflicting-source cases.
