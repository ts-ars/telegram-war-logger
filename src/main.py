"""
README
======

Install dependencies:
  pip install -r requirements.txt

Create .env file with:
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHAT_ID=-100123
  GOOGLE_SHEET_ID=...
  WAR_SHEET_NAME=war
  TIMEZONE=Europe/Warsaw
  CHAT_ID_TO_SEKCJA={"-100123:12":"maszyna","-100123:34":"pakowanie","-100123:56":"kontrola_wagi","-100123:78":"laba"}
  # Optional: PROCESSED_PATH=processed.jsonl

Run:
  python -m src.main
"""

from __future__ import annotations

import asyncio
import logging

from adapters.config.settings import SekcjaResolver, Settings
from adapters.sheets.war_sheet import WarSheetAdapter
from adapters.storage.processed_jsonl import ProcessedJsonlStore
from adapters.telegram.mapper import dto_to_domain, update_to_dto
from adapters.telegram.update_source import TelegramUpdateSource
from application.bootstrap import build_service

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    settings = Settings.from_env()
    sheet = WarSheetAdapter(settings.google_sheet_id, settings.war_sheet_name)
    processed_store = ProcessedJsonlStore(settings.processed_path)
    sekcja_resolver = SekcjaResolver(settings.chat_id_to_sekcja)
    service = build_service(
        sheet=sheet,
        processed_store=processed_store,
        sekcja_resolver=sekcja_resolver,
        timezone_name=settings.timezone,
    )

    update_source = TelegramUpdateSource(settings.telegram_bot_token)

    async def handle_update(update, context) -> None:  # type: ignore[no-untyped-def]
        dto = update_to_dto(update)
        if dto is None:
            return
        if dto.chat_id != settings.telegram_chat_id:
            logger.info("skip message from unknown chat", extra={"chat_id": dto.chat_id})
            return
        message = dto_to_domain(dto)
        service.handle_message(message)

    application = update_source.build_application(handle_update)

    logger.info("bot started")
    await application.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(main())
