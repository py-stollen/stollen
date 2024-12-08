from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

from stollen import Stollen
from stollen.requests import InputFile, Placeholder

if TYPE_CHECKING:
    from .types import LinkPreviewOptions, Message


class TelegramBot(Stollen):
    def __init__(
        self,
        token: str,
        link_preview_disabled: bool = True,
        **stollen_kwargs: Any,
    ) -> None:
        self.token = token
        self.link_preview_disabled = link_preview_disabled
        super().__init__(
            base_url="https://api.telegram.org/bot{token}",
            response_data_key=["result"],
            global_request_fields=[Placeholder(name="token", value=token)],
            **stollen_kwargs,
        )

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[InputFile, str],
        caption: Optional[str] = None,
        link_preview_options: Optional[LinkPreviewOptions] = None,
    ) -> Message:
        from .methods import SendPhoto

        call: SendPhoto = SendPhoto(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            link_preview_options=link_preview_options,
        )

        return await self(call)
