from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from application.ports import ProcessedStorePort, SekcjaResolverPort, WarSheetPort
from domain import parsing
from domain.model import IncomingMessage, ParsedMessage, ProcessedKey

logger = logging.getLogger(__name__)


class WarBotService:
    def __init__(
        self,
        sheet: WarSheetPort,
        processed_store: ProcessedStorePort,
        sekcja_resolver: SekcjaResolverPort,
        timezone: ZoneInfo,
        header_map: dict[str, int],
        processed: set[ProcessedKey],
        cache: dict[str, str],
    ) -> None:
        self._sheet = sheet
        self._processed_store = processed_store
        self._sekcja_resolver = sekcja_resolver
        self._timezone = timezone
        self._header_map = header_map
        self._processed = processed
        self._cache = cache

    def handle_message(self, message: IncomingMessage) -> None:
        key = ProcessedKey(chat_id=message.chat_id, message_id=message.message_id)
        if key in self._processed:
            logger.info("skip message already processed", extra={"message_id": message.message_id})
            return

        sekcja = self._sekcja_resolver.resolve(message.chat_id, message.thread_id)
        if not sekcja:
            logger.info(
                "skip message unknown topic",
                extra={"chat_id": message.chat_id, "thread_id": message.thread_id},
            )
            return

        partia = parsing.extract_partia(message.text)
        if not partia:
            logger.info("skip message no partia", extra={"message_id": message.message_id})
            return

        brutto = parsing.extract_brutto(message.text)
        if brutto is None:
            logger.info("skip message no brutto", extra={"message_id": message.message_id})
            return

        nomenklatura = parsing.extract_nomenklatura(message.text)
        kategoria = self._resolve_kategoria(sekcja, partia, message.text)

        record = ParsedMessage(
            partia=partia,
            brutto=brutto,
            nomenklatura=nomenklatura,
            kategoria=kategoria,
        )

        values_by_header = self._build_values(sekcja, message, record)
        self._sheet.append_row(values_by_header, self._header_map)

        self._processed_store.append_processed(key)
        self._processed.add(key)
        logger.info("appended row", extra={"message_id": message.message_id, "partia": partia})

        if sekcja == "laba" and kategoria:
            self._cache[partia] = kategoria

    def _resolve_kategoria(self, sekcja: str, partia: str, text: str) -> str:
        if sekcja == "laba":
            return parsing.extract_kategoria(text)
        return self._cache.get(partia, "")

    def _build_values(
        self,
        sekcja: str,
        message: IncomingMessage,
        record: ParsedMessage,
    ) -> dict[str, str]:
        timestamp = self._format_datetime(message.date_utc)
        comments = message.text
        if message.has_photo:
            comments = f"{comments} photo:yes".strip()
        return {
            "Data": timestamp,
            "sekcja produkcyjna / produkcja / участок": sekcja,
            "numer partii": record.partia,
            "Kategoria produktu": record.kategoria,
            "nomenklatura / asortyment": record.nomenklatura,
            "wartość faktyczna, faktyczne znaczenie BRUTTO": self._format_decimal(record.brutto),
            "komentarze / uwagi komentarzy / saemachanija": comments,
        }

    def _format_datetime(self, value: datetime) -> str:
        return value.astimezone(self._timezone).strftime("%d.%m.%Y %H:%M:%S")

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value, "f")
