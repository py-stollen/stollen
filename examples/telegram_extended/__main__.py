from __future__ import annotations

import logging

from stollen.requests import FSInputFile

from .client import TelegramBot
from .types import Message


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    async with TelegramBot(token="42:ABC") as bot:  # noqa: S106
        message: Message = await bot.send_photo(
            chat_id=5945468457,
            photo=FSInputFile("/home/wakaree/Downloads/sticker.webp"),
            caption="Hello from Stollen!",
        )
        logging.info(message)
