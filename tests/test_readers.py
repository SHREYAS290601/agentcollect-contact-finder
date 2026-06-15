from __future__ import annotations

import pytest

from contact_finder.readers import read_companies


def test_reads_all_rows_from_companies_csv() -> None:
    companies = read_companies("challenge/data/companies.csv")

    assert len(companies) == 30
    assert companies[0].company_name
    assert companies[0].mailing_address


def test_missing_file_raises_clear_error() -> None:
    with pytest.raises(FileNotFoundError, match="Company CSV not found"):
        read_companies("challenge/data/missing-companies.csv")


def test_missing_required_columns_raises_clear_error(tmp_path) -> None:
    csv_path = tmp_path / "companies.csv"
    csv_path.write_text("company_name\nExample Co\n", encoding="utf-8")

    with pytest.raises(ValueError, match="mailing_address"):
        read_companies(csv_path)
