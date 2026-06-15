from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPANIES_PATH = "challenge/data/companies.csv"
MOCKS_PATH = "challenge/mocks/enrichment_responses.json"


def test_cli_runs_full_pipeline_with_real_challenge_data(tmp_path) -> None:
    output_path = tmp_path / "contact_finder_results.csv"

    completed = _run_cli(output_path)

    assert completed.returncode == 0
    assert "Input rows processed: 30" in completed.stdout
    assert output_path.exists()

    input_rows = _read_csv(REPO_ROOT / COMPANIES_PATH)
    output_rows = _read_csv(output_path)

    assert len(output_rows) == len(input_rows)
    assert any(row["contact_email_or_phone"] for row in output_rows)
    assert any(
        row["needs_human_review"] == "true" and row["contact_email_or_phone"] == ""
        for row in output_rows
    )

    desert_sky = _row_for_company(output_rows, "Desert Sky Solar")
    assert desert_sky["needs_human_review"] == "true"
    assert desert_sky["contact_email_or_phone"] == ""
    assert desert_sky["confidence_score"] == "0"

    riverside = _row_for_company(output_rows, "Riverside Print & Sign")
    assert riverside["contact_role"] == ""
    assert riverside["contact_email_or_phone"] == ""
    assert 0 < int(riverside["confidence_score"]) < 70

    lakeside = _row_for_company(output_rows, "Lakeside Auto Glass")
    assert lakeside["contact_name"] == "Jeff"
    assert lakeside["contact_role"] == "Manager"
    assert lakeside["contact_email_or_phone"] == ""


def test_cli_limit_writes_limited_number_of_rows(tmp_path) -> None:
    output_path = tmp_path / "limited_results.csv"

    completed = _run_cli(output_path, "--limit", "5")

    assert completed.returncode == 0
    assert "Input rows processed: 5" in completed.stdout
    assert len(_read_csv(output_path)) == 5


def _run_cli(output_path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "contact_finder.cli",
            "--companies",
            COMPANIES_PATH,
            "--mocks",
            MOCKS_PATH,
            "--output",
            str(output_path),
            *extra_args,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def _row_for_company(rows: list[dict[str, str]], company_name: str) -> dict[str, str]:
    return next(row for row in rows if row["company_name"] == company_name)
