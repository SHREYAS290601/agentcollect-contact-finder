# AgentCollect Contact Finder Challenge

This is my submission for the AgentCollect hiring challenge.

The solution implements a small, deterministic contact-resolution pipeline for the provided company records and mock enrichment data. It reads input companies, looks up mock provider evidence, normalizes the evidence, resolves one defensible contact when possible, scores confidence, routes weak/conflicting records to human review, and writes a final CSV output.

## Approach

The main goal was precision over coverage. I avoided inventing contacts or over-merging weak evidence. If evidence was missing, generic, conflicting, or below the confidence threshold, the system keeps the row in the output but blanks the contact method and marks it for human review.

The pipeline uses:

* exact company-name lookup into the mock provider JSON
* normalized provider evidence across registry, listing, and enrichment data
* conservative name matching with support for exact matches, limited soft matches, and conflict detection
* confidence scoring based on provider agreement, role quality, contactability, generic emails, source conflicts, and enrichment confidence
* provenance preservation through source URLs
* CSV output with one row per input company

## Project structure

```text
contact_finder/
  cli.py          # command-line entry point
  matching.py     # shared name/email matching helpers
  models.py       # dataclasses for companies, evidence, and resolved contacts
  normalizer.py   # provider bundle to normalized evidence
  providers.py    # mock provider loader
  readers.py      # input CSV reader
  resolver.py     # contact selection and review routing
  scorer.py       # confidence scoring
  writer.py       # output CSV writer

tests/
  test_*.py       # unit and CLI tests

outputs/
  contact_finder_results.csv  # sample generated output
```

## Run the pipeline

From the repository root:

```bash
python3 -m contact_finder.cli \
  --companies challenge/data/companies.csv \
  --mocks challenge/mocks/enrichment_responses.json \
  --output outputs/contact_finder_results.csv
```

Optional limit:

```bash
python3 -m contact_finder.cli \
  --companies challenge/data/companies.csv \
  --mocks challenge/mocks/enrichment_responses.json \
  --output outputs/contact_finder_results.csv \
  --limit 5
```

## Run tests

```bash
python3 -m pytest
```

## Output

The generated output is written to:

```text
outputs/contact_finder_results.csv
```

Output columns:

```text
company_name,contact_name,contact_role,contact_email_or_phone,confidence_score,source,needs_human_review
```

A contact method is only emitted when the score passes the review threshold. Low-confidence or conflicting rows are still included, but marked with `needs_human_review=true`.

## Notes

* No real APIs or scraping are used.
* Missing mock responses are treated as cannot-verify rows, not errors.
* Generic business contacts are penalized and generally routed to review unless enough supporting evidence exists.
* Conflicting person evidence is routed to review.
* `PLAN.md` was committed before implementation work, as requested.
* `ABOUT.md` contains the reflective writeup requested in the challenge.
