from __future__ import annotations

import csv
from pathlib import Path

from contact_finder.models import CompanyInput


REQUIRED_COMPANY_COLUMNS = {"company_name", "mailing_address"}


def read_companies(path: str | Path) -> list[CompanyInput]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Company CSV not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COMPANY_COLUMNS - fieldnames
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required company CSV column(s): {missing}")

        return [
            CompanyInput(
                company_name=(row.get("company_name") or "").strip(),
                mailing_address=(row.get("mailing_address") or "").strip(),
            )
            for row in reader
        ]
