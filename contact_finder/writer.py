from __future__ import annotations

import csv
from pathlib import Path

from contact_finder.models import ResolvedContact


FIELDNAMES = [
    "company_name",
    "contact_name",
    "contact_role",
    "contact_email_or_phone",
    "confidence_score",
    "source",
    "needs_human_review",
]


def write_results(path: str | Path, results: list[ResolvedContact]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "company_name": result.company_name,
                    "contact_name": _value_or_empty(result.contact_name),
                    "contact_role": _value_or_empty(result.contact_role),
                    "contact_email_or_phone": _value_or_empty(
                        result.contact_email_or_phone
                    ),
                    "confidence_score": result.confidence_score,
                    "source": result.source,
                    "needs_human_review": str(result.needs_human_review).lower(),
                }
            )


def _value_or_empty(value: str | None) -> str:
    return value if value is not None else ""
