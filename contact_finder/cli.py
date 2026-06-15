from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from contact_finder.normalizer import normalize_provider_bundle
from contact_finder.providers import MockProviderLoader
from contact_finder.readers import read_companies
from contact_finder.resolver import resolve_contact
from contact_finder.writer import write_results


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    companies = read_companies(args.companies)
    if args.limit is not None:
        companies = companies[: args.limit]

    provider_loader = MockProviderLoader(args.mocks)
    results = []
    for company in companies:
        bundle = provider_loader.get_for_company(company.company_name)
        evidence = normalize_provider_bundle(bundle)
        results.append(resolve_contact(company.company_name, evidence))

    write_results(args.output, results)
    _print_summary(Path(args.output), results)
    return 0


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve Stage B contact finder results.")
    parser.add_argument("--companies", required=True, help="Path to companies CSV")
    parser.add_argument("--mocks", required=True, help="Path to mock provider JSON")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--limit", type=_non_negative_int, help="Optional row limit")
    return parser.parse_args(argv)


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("--limit must be non-negative")
    return parsed


def _print_summary(output_path: Path, results) -> None:
    usable_contacts = sum(1 for result in results if result.contact_email_or_phone)
    human_review_rows = sum(1 for result in results if result.needs_human_review)

    print(f"Input rows processed: {len(results)}")
    print(f"Usable contacts emitted: {usable_contacts}")
    print(f"Human review rows: {human_review_rows}")
    print(f"Output path: {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
