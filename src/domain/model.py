from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

REQUIRED_HEADERS = [
    "Data",
    "sekcja produkcyjna / produkcja / участок",
    "numer partii",
    "Kategoria produktu",
    "nomenklatura / asortyment",
    "data produkcji nikotyny / partia",
    "maszyna",
    "wartość faktyczna, faktyczne znaczenie BRUTTO",
    "brak produkcyjny / niezgodny",
    "liczba netto",
    "komentarze / uwagi komentarzy / saemachanija",
]


@dataclass(frozen=True)
class IncomingMessage:
    chat_id: int
    message_id: int
    thread_id: int | None
    text: str
    date_utc: datetime
    has_photo: bool


@dataclass(frozen=True)
class ProcessedKey:
    chat_id: int
    message_id: int


@dataclass(frozen=True)
class ParsedMessage:
    partia: str
    brutto: Decimal
    nomenklatura: str
    kategoria: str
