from typing import Optional, Union

from stollen.requests import BodyField, InputFile

from ..defaults import default_link_preview_options
from ..types import LinkPreviewOptions, Message
from .base import TelegramMethod


class SendPhoto(
    TelegramMethod[Message],
    api_method="/sendPhoto",
    returning=Message,
):
    chat_id: Union[int, str]
    photo: Union[InputFile, str]
    caption: Optional[str] = None
    link_preview_options: Optional[LinkPreviewOptions] = BodyField(
        field_factory=default_link_preview_options,
    )
