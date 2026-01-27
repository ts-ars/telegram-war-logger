from __future__ import annotations

from telegram import Update

from adapters.telegram.dto import TelegramMessageData
from domain.model import IncomingMessage


def update_to_dto(update: Update) -> TelegramMessageData | None:
    message = update.message
    if message is None:
        return None
    text = message.text or message.caption or ""
    return TelegramMessageData(
        chat_id=message.chat_id,
        message_id=message.message_id,
        thread_id=message.message_thread_id,
        text=text,
        date_utc=message.date,
        has_photo=bool(message.photo),
    )


def dto_to_domain(dto: TelegramMessageData) -> IncomingMessage:
    return IncomingMessage(
        chat_id=dto.chat_id,
        message_id=dto.message_id,
        thread_id=dto.thread_id,
        text=dto.text,
        date_utc=dto.date_utc,
        has_photo=dto.has_photo,
    )
