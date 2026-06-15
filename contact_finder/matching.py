from __future__ import annotations

import re


GENERIC_EMAIL_PREFIXES = {
    "info",
    "contact",
    "sales",
    "office",
    "hello",
    "admin",
    "support",
    "service",
}
NICKNAME_PAIRS = {
    frozenset({"robert", "bob"}),
}


def normalize_name(name: str | None) -> str | None:
    if not name:
        return None

    without_parenthetical = name.split("(", 1)[0]
    cleaned = re.sub(r"[^a-zA-Z\s.]", " ", without_parenthetical).casefold()
    parts = [part for part in cleaned.replace(".", " ").split() if part]
    if parts and parts[0] in {"dr", "mr", "mrs", "ms"}:
        parts = parts[1:]
    return " ".join(parts) or None


def is_generic_email(email: str | None) -> bool:
    if not email or "@" not in email:
        return False
    return email.split("@", 1)[0].casefold() in GENERIC_EMAIL_PREFIXES


def names_match(name_a: str | None, name_b: str | None) -> str:
    normalized_a = normalize_name(name_a)
    normalized_b = normalize_name(name_b)
    if not normalized_a or not normalized_b:
        return "unknown"
    if normalized_a == normalized_b:
        return "exact"

    parts_a = normalized_a.split()
    parts_b = normalized_b.split()
    if len(parts_a) < 2 or len(parts_b) < 2:
        return "unknown"

    first_a = parts_a[0]
    first_b = parts_b[0]
    if parts_a[-1] != parts_b[-1]:
        return "conflict"
    if _are_known_nickname_variants(first_a, first_b):
        return "soft"
    if _is_initial(first_a) and first_a[0] == first_b[0]:
        return "soft"
    if _is_initial(first_b) and first_b[0] == first_a[0]:
        return "soft"
    return "conflict"


def email_matches_name(email: str, name: str) -> bool:
    normalized_name = normalize_name(name)
    if not normalized_name or "@" not in email:
        return False

    local_part = email.split("@", 1)[0].casefold()
    local_tokens = [token for token in re.split(r"[^a-z]+", local_part) if token]
    compact_local = "".join(local_tokens)
    name_parts = normalized_name.split()
    first_name = name_parts[0]
    first_aliases = _first_name_aliases(first_name)

    if len(name_parts) == 1:
        return compact_local in first_aliases

    last_name = name_parts[-1]
    if any(alias in local_tokens for alias in first_aliases):
        return True
    if first_name[0] in local_tokens and last_name in local_tokens:
        return True
    return any(
        compact_local == f"{alias}{last_name}" or compact_local == f"{alias[0]}{last_name}"
        for alias in first_aliases
    )


def _are_known_nickname_variants(first_a: str, first_b: str) -> bool:
    return frozenset({first_a, first_b}) in NICKNAME_PAIRS


def _is_initial(first_name: str) -> bool:
    return len(first_name) == 1


def _first_name_aliases(first_name: str) -> set[str]:
    aliases = {first_name}
    if first_name == "robert":
        aliases.add("bob")
    elif first_name == "bob":
        aliases.add("robert")
    return aliases
