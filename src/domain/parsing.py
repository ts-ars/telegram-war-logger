from __future__ import annotations

import re
from decimal import Decimal

PARTIA_REGEX = re.compile(r"A\d{5}")
NUMBER_REGEX = re.compile(r"\d+(?:[.,]\d+)?")
KATEGORIA_REGEX = re.compile(r"(?i)(?:^|\b)(?:kat|kategoria):\s*(.+)")


def extract_partia(text: str) -> str | None:
    match = PARTIA_REGEX.search(text)
    return match.group(0) if match else None


def find_brutto_match(text: str) -> re.Match[str] | None:
    return NUMBER_REGEX.search(text)


def extract_brutto(text: str) -> Decimal | None:
    match = find_brutto_match(text)
    if not match:
        return None
    value = match.group(0).replace(",", ".")
    try:
        return Decimal(value)
    except Exception:
        return None


def extract_nomenklatura(text: str) -> str:
    partia_match = PARTIA_REGEX.search(text)
    brutto_match = find_brutto_match(text)
    spans = []
    if partia_match:
        spans.append(partia_match.span())
    if brutto_match:
        spans.append(brutto_match.span())
    if not spans:
        return text.strip()
    spans.sort()
    result_parts: list[str] = []
    last_index = 0
    for start, end in spans:
        if start > last_index:
            result_parts.append(text[last_index:start])
        last_index = end
    if last_index < len(text):
        result_parts.append(text[last_index:])
    return "".join(result_parts).strip()


def extract_kategoria(text: str) -> str:
    match = KATEGORIA_REGEX.search(text)
    if not match:
        return ""
    value = match.group(1).strip()
    if not value:
        return ""
    return value.splitlines()[0].strip()
