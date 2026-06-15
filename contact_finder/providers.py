from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MockProviderLoader:
    def __init__(self, path: str | Path):
        mock_path = Path(path)
        if not mock_path.exists():
            raise FileNotFoundError(f"Mock provider JSON not found: {mock_path}")

        try:
            with mock_path.open(encoding="utf-8") as mock_file:
                data = json.load(mock_file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid mock provider JSON: {mock_path}") from exc

        if not isinstance(data, dict):
            raise ValueError(f"Mock provider JSON must contain an object: {mock_path}")

        self._data: dict[str, dict[str, Any]] = data

    def get_for_company(self, company_name: str) -> dict | None:
        return self._data.get(company_name)
