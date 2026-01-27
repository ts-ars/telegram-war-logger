from __future__ import annotations

from typing import Awaitable, Callable

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, MessageHandler, filters


class TelegramUpdateSource:
    def __init__(self, token: str) -> None:
        self._token = token

    def build_application(
        self, handler: Callable[[Update], Awaitable[None]]
    ) -> Application:
        application = ApplicationBuilder().token(self._token).build()
        application.add_handler(
            MessageHandler(filters.TEXT | filters.PHOTO, handler)
        )
        return application
