from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Optional, Union

from stollen import Stollen, StollenMethod, StollenObject
from stollen.enums import HTTPMethod
from stollen.requests.fields import Placeholder
from stollen.requests.input_file import FSInputFile, InputFile


class Bot(Stollen):
    def __init__(self, token: str) -> None:
        self.token = token
        super().__init__(
            base_url="https://api.telegram.org/bot{token}",
            response_data_key=["result"],
            global_request_fields=[
                lambda stollen, request: Placeholder(name="token", value=token),
            ],
        )

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[InputFile, str],
        caption: Optional[str] = None,
    ) -> Message:
        call: SendPhoto = SendPhoto(chat_id=chat_id, photo=photo, caption=caption)
        return await self(call)


class PhotoSize(StollenObject[Bot]):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None


class Message(StollenObject[Bot]):
    message_id: int
    date: datetime
    photo: Optional[list[PhotoSize]] = None
    caption: Optional[str] = None


class SendPhoto(
    StollenMethod[Message, Bot],
    http_method=HTTPMethod.POST,
    api_method="/sendPhoto",
    returning=Message,
):
    chat_id: Union[int, str]
    photo: Union[InputFile, str]
    caption: Optional[str] = None


async def main() -> None:
    """
    Thanks to @JRootJunior for the pretty Telegram bot framework! ❤️
    """
    logging.basicConfig(level=logging.DEBUG)
    async with Bot(token="42:ABC") as bot:  # noqa: S106
        message: Message = await bot.send_photo(
            chat_id=5945468457,
            photo=FSInputFile("/home/wakaree/Downloads/sticker.webp"),
            caption="Hello from Stollen!",
        )
        logging.info(message)


if __name__ == "__main__":
    asyncio.run(main())
