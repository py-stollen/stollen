from typing import Optional

from .base import TelegramObject


class PhotoSize(TelegramObject):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None
