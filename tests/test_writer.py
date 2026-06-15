from __future__ import annotations

import csv

from contact_finder.models import ResolvedContact
from contact_finder.writer import FIELDNAMES, write_results


def test_write_results_writes_expected_header(tmp_path) -> None:
    output_path = tmp_path / "nested" / "results.csv"

    write_results(output_path, [])

    header = output_path.read_text(encoding="utf-8").splitlines()[0]
    assert header == ",".join(FIELDNAMES)


def test_write_results_writes_one_row_per_resolved_contact(tmp_path) -> None:
    output_path = tmp_path / "results.csv"
    results = [
        ResolvedContact(
            company_name="Cedar Ridge Plumbing LLC",
            contact_name="Daniel Ortega",
            contact_role="Owner",
            contact_email_or_phone="d.ortega@cedarridgeplumbing.com",
            confidence_score=94,
            source="registry:mock://registry/example",
            needs_human_review=False,
        ),
        ResolvedContact(
            company_name="Desert Sky Solar",
            contact_name=None,
            contact_role=None,
            contact_email_or_phone=None,
            confidence_score=0,
            source="",
            needs_human_review=True,
        ),
    ]

    write_results(output_path, results)

    with output_path.open(newline="", encoding="utf-8") as output_file:
        rows = list(csv.DictReader(output_file))

    assert len(rows) == 2
    assert rows[0]["company_name"] == "Cedar Ridge Plumbing LLC"
    assert rows[1]["company_name"] == "Desert Sky Solar"


def test_write_results_converts_none_fields_to_empty_strings(tmp_path) -> None:
    output_path = tmp_path / "results.csv"
    result = ResolvedContact(
        company_name="Desert Sky Solar",
        contact_name=None,
        contact_role=None,
        contact_email_or_phone=None,
        confidence_score=0,
        source="",
        needs_human_review=True,
    )

    write_results(output_path, [result])

    with output_path.open(newline="", encoding="utf-8") as output_file:
        row = next(csv.DictReader(output_file))

    assert row["contact_name"] == ""
    assert row["contact_role"] == ""
    assert row["contact_email_or_phone"] == ""


def test_write_results_writes_review_booleans_as_lowercase_strings(tmp_path) -> None:
    output_path = tmp_path / "results.csv"
    results = [
        ResolvedContact(
            company_name="Known Co",
            contact_name="Known Person",
            contact_role="Owner",
            contact_email_or_phone="known@example.com",
            confidence_score=90,
            source="enrichment:mock://enrichment/known",
            needs_human_review=False,
        ),
        ResolvedContact(
            company_name="Review Co",
            contact_name=None,
            contact_role=None,
            contact_email_or_phone=None,
            confidence_score=20,
            source="",
            needs_human_review=True,
        ),
    ]

    write_results(output_path, results)

    with output_path.open(newline="", encoding="utf-8") as output_file:
        rows = list(csv.DictReader(output_file))

    assert rows[0]["needs_human_review"] == "false"
    assert rows[1]["needs_human_review"] == "true"
