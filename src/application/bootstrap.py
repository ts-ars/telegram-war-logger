from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

from application.ports import ProcessedStorePort, SekcjaResolverPort, WarSheetPort
from application.services import WarBotService
from domain import parsing

logger = logging.getLogger(__name__)


def build_service(
    sheet: WarSheetPort,
    processed_store: ProcessedStorePort,
    sekcja_resolver: SekcjaResolverPort,
    timezone_name: str,
) -> WarBotService:
    header_map = sheet.read_header_map()
    sheet.validate_required_headers(header_map)

    processed = processed_store.load_processed()
    cache = build_kategoria_cache(sheet)

    logger.info(
        "service initialized",
        extra={"processed_count": len(processed), "cache_size": len(cache)},
    )

    timezone = ZoneInfo(timezone_name)
    return WarBotService(
        sheet=sheet,
        processed_store=processed_store,
        sekcja_resolver=sekcja_resolver,
        timezone=timezone,
        header_map=header_map,
        processed=processed,
        cache=cache,
    )


def build_kategoria_cache(sheet: WarSheetPort) -> dict[str, str]:
    rows = sheet.read_rows_for_cache()
    cache: dict[str, str] = {}
    for row in rows:
        sekcja = row.get("sekcja produkcyjna / produkcja / участок", "")
        if sekcja != "laba":
            continue
        partia = parsing.extract_partia(row.get("numer partii", ""))
        if not partia:
            continue
        kategoria = row.get("Kategoria produktu", "")
        if kategoria:
            cache[partia] = kategoria
    return cache
