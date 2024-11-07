from datetime import datetime
from typing import Optional

from .base import TelegramObject
from .photo_size import PhotoSize


class Message(TelegramObject):
    message_id: int
    date: datetime
    photo: Optional[list[PhotoSize]] = None
    caption: Optional[str] = None
