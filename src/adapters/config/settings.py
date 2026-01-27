from __future__ import annotations

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: int
    google_sheet_id: str
    war_sheet_name: str
    timezone: str
    chat_id_to_sekcja: dict[str, str]
    processed_path: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        telegram_bot_token = _require_env("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = int(_require_env("TELEGRAM_CHAT_ID"))
        google_sheet_id = _require_env("GOOGLE_SHEET_ID")
        war_sheet_name = os.getenv("WAR_SHEET_NAME", "war")
        timezone = os.getenv("TIMEZONE", "Europe/Warsaw")
        mapping_raw = _require_env("CHAT_ID_TO_SEKCJA")
        chat_id_to_sekcja = json.loads(mapping_raw)
        processed_path = os.getenv("PROCESSED_PATH", "processed.jsonl")
        return cls(
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            google_sheet_id=google_sheet_id,
            war_sheet_name=war_sheet_name,
            timezone=timezone,
            chat_id_to_sekcja=chat_id_to_sekcja,
            processed_path=processed_path,
        )

    def resolve_sekcja(self, chat_id: int, thread_id: int | None) -> str | None:
        key = f"{chat_id}:{thread_id}"
        return self.chat_id_to_sekcja.get(key)


@dataclass(frozen=True)
class SekcjaResolver:
    mapping: dict[str, str]

    def resolve(self, chat_id: int, thread_id: int | None) -> str | None:
        key = f"{chat_id}:{thread_id}"
        return self.mapping.get(key)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
