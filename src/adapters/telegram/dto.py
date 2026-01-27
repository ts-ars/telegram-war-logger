from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TelegramMessageData:
    chat_id: int
    message_id: int
    thread_id: int | None
    text: str
    date_utc: datetime
    has_photo: bool
